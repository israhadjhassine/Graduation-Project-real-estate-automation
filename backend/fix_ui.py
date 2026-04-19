import re
import os

file_path = r'c:\real-estate-automation\frontend\app\components\property\UploadModal.vue'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the target and replacement using regex to handle whitespace/indentation variations
# We look for the select with form.city and update its class and style
pattern = r'(<select v-model="form\.city" .*?class="form-input)\s+(pl-\d+|!pl-\d+)?\s*(appearance-none.*?>)'
replacement = r'\1 !pl-16 appearance-none cursor-pointer" style="padding-left: 4rem !important;">'

new_content = re.sub(pattern, replacement, content)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully updated UploadModal.vue")
else:
    print("Could not find the target pattern in UploadModal.vue")
