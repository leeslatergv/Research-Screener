# --- R Script for Google Scholar Batch Data Retrieval with PAGINATION ---
# This version fetches multiple pages for each search query.

# --- 1. Loading Required Libraries ---
if (!requireNamespace("httr", quietly = TRUE)) install.packages("httr")
if (!requireNamespace("jsonlite", quietly = TRUE)) install.packages("jsonlite")
if (!requireNamespace("dplyr", quietly = TRUE)) install.packages("dplyr")

library(httr)
library(jsonlite)
library(dplyr)

# --- 2. Configuration ---

# !!! IMPORTANT: Replace "YOUR_API_KEY" with your key from the SerpApi dashboard !!!
api_key <- "78b850b977adea90d1551bea9d20f8a1e9181a041125af461016c259cc4fe617" 

# --- NEW: Set how many pages you want to fetch for each protocol ---
# Each page has ~10 results, so 10 pages = ~100 results.
num_pages_to_fetch <- 10

# Your list of search queries (unchanged)
search_protocols <- c(
  '("financial incentive" OR scholarship OR bursary OR "loan forgiveness" OR stipend) AND ("health profession education" OR "medical education" OR "nursing education") AND (recruitment OR enrollment OR enrolment)',
  '("financial aid" OR "tuition reimbursement") AND ("health student" OR "medical student" OR "nursing student") AND (recruitment OR enrollment OR application)',
  '("loan forgiveness" OR "loan repayment") AND ("health profession" OR "medical school" OR "nursing school") AND (recruitment OR enrollment)',
  '("tuition reimbursement" OR "tuition waiver" OR "fee waiver") AND ("health education" OR "medical training") AND (enrollment OR matriculation)',
  '(bursary OR bursaries OR stipend) AND ("health profession student" OR "medical student") AND (recruitment OR "career choice")',
  '("financial incentive" OR scholarship) AND ("health career" OR "healthcare education") AND ("decision to enroll" OR "application numbers")',
  '("financial support" OR scholarship) AND ("recruiting students" OR "student recruitment") AND ("medical school" OR "nursing school" OR "allied health")',
  '("education funding" OR scholarship) AND (recruitment OR enrollment) AND ("health workforce" OR "healthcare workforce")',
  'effectiveness of financial incentives AND "health profession education" AND recruitment',
  'impact of scholarships on enrollment AND ("medical students" OR "nursing students")',
  'loan forgiveness program AND "health profession student" recruitment',
  '(scholarship OR bursary) AND ("allied health education" OR "medical school" OR "nursing school") AND ("student application" OR "university admission" OR "program choice")'
)

timestamp <- format(Sys.time(), "%Y-%m-%d_%H-%M-%S")
output_filename <- paste0("scholar_results_paginated_api_", timestamp, ".json")
serpapi_url <- "https://serpapi.com/search.json"
all_results_list <- list()

# --- 3. Main Data Retrieval Loop ---

cat("Starting Google Scholar data retrieval via direct API calls...\n")
if (api_key == "YOUR_API_KEY") {
  stop("Execution halted. Please replace 'YOUR_API_KEY' with your actual SerpApi key.")
}

# Outer loop: Iterates through each of your search protocols
for (protocol_index in 1:length(search_protocols)) {
  
  search_query <- search_protocols[protocol_index]
  cat(sprintf("\n--- Starting Protocol %d of %d ---\nQuery: %s\n", protocol_index, length(search_protocols), search_query))
  
  # --- NEW: Inner loop to handle pagination for the current protocol ---
  for (page_num in 1:num_pages_to_fetch) {
    
    # Calculate the 'start' index for the current page
    start_index <- (page_num - 1) * 10
    
    cat(sprintf("   -> Fetching page %d (start index %d)...\n", page_num, start_index))
    
    query_params <- list(
      engine = "google_scholar",
      q = search_query,
      start = start_index, # The crucial parameter for pagination
      api_key = api_key
    )
    
    response <- tryCatch({
      GET(url = serpapi_url, query = query_params)
    }, error = function(e) {
      cat(sprintf("      [!] Connection Error: %s\n", e$message))
      return(NULL)
    })
    
    # Check if the API call failed
    if (is.null(response) || http_status(response)$category != "Success") {
      cat("      [!] API request failed. Stopping this protocol and moving to the next.\n")
      break # Exit the inner pagination loop
    }
    
    # Extract and parse the JSON content
    response_content <- content(response, "text", encoding = "UTF-8")
    search_results <- fromJSON(response_content, flatten = TRUE)
    
    # Check if the page has results. If not, stop trying to get more pages.
    if (!is.null(search_results$organic_results) && nrow(as.data.frame(search_results$organic_results)) > 0) {
      
      results_df <- as.data.frame(search_results$organic_results)
      cat(sprintf("      Successfully retrieved %d results from this page.\n", nrow(results_df)))
      
      # Add our tracking data
      results_df$protocol_id <- protocol_index
      results_df$source_query <- search_query
      results_df$page_number <- page_num # Also track which page it came from
      
      all_results_list[[length(all_results_list) + 1]] <- results_df
      
    } else {
      # This is the "no more results" condition
      cat("      No more results found for this protocol. Moving to the next one.\n")
      break # Exit the inner pagination loop
    }
    
    # A short, polite pause between fetching pages of the same query
    Sys.sleep(runif(1, 2, 4))
    
  } # --- End of inner pagination loop ---
  
} # --- End of outer protocol loop ---


# --- 4. Exporting Data to JSON ---

cat("\nAll data retrieval protocols complete.\n")
if (length(all_results_list) > 0) {
  final_results_df <- bind_rows(all_results_list)
  
  json_output <- toJSON(final_results_df, pretty = TRUE, auto_unbox = FALSE, dataframe = "rows")
  write(json_output, output_filename)
  
  cat(sprintf("Successfully exported %d total results from all protocols to '%s'\n", nrow(final_results_df), output_filename))
} else {
  cat("No results were collected. No JSON file was created.\n")
}