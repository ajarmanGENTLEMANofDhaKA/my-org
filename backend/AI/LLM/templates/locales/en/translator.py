from string import Template

###System prompt
system_prompt = Template("\n".join([
    "You are a helpful assistant for translating text",
    "You will translate the provided text to the target language",
    "Make sure you will return the translated text only"
]))

###Document prompt
document_prompt = Template("\n".join([
    "The text will be translated: $text",
    "The target language: $target_language"

]))

###Footer prompt
footer_prompt = Template("\n".join([
    "The tanslated text: ",
]))