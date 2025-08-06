# --- R Script for Google Scholar Batch Data Retrieval via SerpApi ---

# --- 1. Installation and Loading of Required Libraries ---
if (!requireNamespace("serpapi", quietly = TRUE)) {
  install.packages("serpapi")
}
if (!requireNamespace("jsonlite", quietly = TRUE)) {
  install.packages("jsonlite")
}
if (!requireNamespace("dplyr", quietly = TRUE)) {
  install.packages("dplyr")
}

library(serpapi)
library(jsonlite)
library(dplyr)

# --- 2. Configuration ---

# !!! IMPORTANT: Replace "YOUR_API_KEY" with the key from your SerpApi dashboard !!!
api_key <- "78b850b977adea90d1551bea9d20f8a1e9181a041125af461016c259cc4fe617" 

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
output_filename <- paste0("scholar_results_serpapi_", timestamp, ".json")

# List to hold all the results data frames
all_results_list <- list()

# --- 3. Main Data Retrieval Loop ---

cat("Starting Google Scholar data retrieval via SerpApi...\n")
if (api_key == "YOUR_API_KEY") {
  stop("Please replace 'YOUR_API_KEY' with your actual SerpApi key.")
}

for (protocol_index in 1:length(search_protocols)) {
  
  search_query <- search_protocols[protocol_index]
  cat(sprintf("\n--- Starting Protocol %d of %d ---\nQuery: %s\n", protocol_index, length(search_protocols), search_query))
  
  # Set up the parameters for the API call
  params <- list(
    engine = "google_scholar", # Specify the search engine
    q = search_query,          # Your search query
    api_key = api_key
  )
  
  # Use SerpApi to get the search results
  search_results <- tryCatch({
    get_json(params)
  }, error = function(e) {
    cat(sprintf("   [!] API Error: %s\n", e$message))
    return(NULL)
  })
  
  if (!is.null(search_results) && !is.null(search_results$organic_results)) {
    # Extract the relevant data frame
    results_df <- search_results$organic_results
    cat(sprintf("   Successfully retrieved %d results.\n", nrow(results_df)))
    
    # Add our tracking data
    results_df$protocol_id <- protocol_index
    results_df$source_query <- search_query
    
    all_results_list[[length(all_results_list) + 1]] <- results_df
  } else {
    cat("   No results found or an API error occurred.\n")
  }
  
  # You don't need long pauses, but a short one is still polite to the API service
  Sys.sleep(runif(1, 2, 5))
}


# --- 4. Exporting Data to JSON ---

cat("\nAll data retrieval protocols complete.\n")
if (length(all_results_list) > 0) {
  # Combine the list of data frames into one
  final_results_df <- bind_rows(all_results_list)
  
  # The API provides rich data, you can select which columns to keep
  # For example: title, link, snippet, publication_info.summary, etc.
  
  json_output <- toJSON(final_results_df, pretty = TRUE, auto_unbox = FALSE, dataframe = "rows")
  write(json_output, output_filename)
  
  cat(sprintf("Successfully exported %d total results to '%s'\n", nrow(final_results_df), output_filename))
} else {
  cat("No results were collected. No JSON file was created.\n")
}