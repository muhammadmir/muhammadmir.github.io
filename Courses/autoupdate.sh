#!/bin/bash

# Update a specific file to a GitHub repo

# Set the file to update
file_to_update="table.json"

# Set the repo URL
repo_url="https://github.com/muhammadmir/muhammadmir.github.io"

# Make sure git is installed
if ! [ -x "$(command -v git)" ]; then
  echo 'Error: git is not installed.' >&2
  exit 1
fi

# Change to the directory containing the file
cd "$(dirname "$file_to_update")"

# Initialize the repo if it's not already
if [ ! -d ".git" ]; then
  git init
  git remote add origin "$repo_url"
fi

# Add the file to the repo
git add "$(basename "$file_to_update")"

# Commit the file with a message
git commit -m "Update $(basename "$file_to_update")"

# Push the file to the repo
git push origin master

# Confirm that the file was pushed
echo "Successfully pushed $(basename "$file_to_update") to $repo_url"
