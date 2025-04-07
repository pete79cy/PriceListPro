#!/bin/bash

# Function to add proper JSON error handling
fix_json_parsing() {
  local file=$1
  local temp_file=$(mktemp)
  
  # Create a sed script to replace direct response.json() calls with proper error handling
  sed 's/\.then(response => response\.json())/\.then(response => {\
    return response.text().then(text => {\
        try {\
            return JSON.parse(text);\
        } catch (err) {\
            console.error("Error parsing JSON:", err);\
            console.log("Raw response:", text);\
            throw new Error("Error parsing server response. Please try again.");\
        }\
    });\
})/g' "$file" > "$temp_file"
  
  # Check if the changes were made
  if cmp -s "$file" "$temp_file"; then
    echo "No changes in $file"
  else
    cp "$temp_file" "$file"
    echo "Updated $file"
  fi
  
  rm "$temp_file"
}

# Files to process
fix_json_parsing "static/js/ai_insights.js"
fix_json_parsing "static/js/ai_feedback.js"
fix_json_parsing "static/js/search.js"

echo "JSON parsing fixes completed"
