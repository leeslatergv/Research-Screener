// assets/hotkeys.js

document.addEventListener('keydown', function(event) {
    // We don't want to trigger hotkeys if the user is typing in an input field
    const activeElement = document.activeElement;
    if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA')) {
        return;
    }

    // Find the buttons in the document
    const keepButton = document.getElementById('keep-btn');
    const discardButton = document.getElementById('discard-btn');
    const prevButton = document.getElementById('prev-btn');
    const nextButton = document.getElementById('next-btn');

    // Check which key was pressed and trigger a click on the corresponding button
    switch (event.key) {
        case '2': // '2' key for "Keep"
            // Check if the button exists and is not disabled before clicking
            if (keepButton) {
                console.log('Keep hotkey pressed');
                keepButton.click();
            }
            break;
            
        case '1': // '1' key for "Discard"
            if (discardButton) {
                console.log('Discard hotkey pressed');
                discardButton.click();
            }
            break;
            
        case 'ArrowRight': // Right arrow for "Next"
            // Prevent the default browser action for arrow keys (like scrolling)
            event.preventDefault(); 
            if (nextButton && !nextButton.disabled) {
                console.log('Next hotkey pressed');
                nextButton.click();
            }
            break;
            
        case 'ArrowLeft': // Left arrow for "Previous"
            event.preventDefault();
            if (prevButton && !prevButton.disabled) {
                console.log('Previous hotkey pressed');
                prevButton.click();
            }
            break;
    }
});