from string import Template

###System prompt
system_prompt = Template("\n".join([
    "You are an expert educator who explains complex concepts in simple, easy-to-understand terms.",
    "Provide a detailed technical explanation of the text, including technical concepts, and in-depth analysis.",
    "Use clear examples and analogies to illustrate key points.",
]))

###Document prompt without context
document_prompt = Template("\n".join([
    "Explain the following text in detail:",
    "$text",
]))

###Document prompt with context
document_prompt_with_context = Template("\n".join([
    "Explain the following text in detail, using the provided context to enhance the explanation:",
    "Context: $context",
    "Text: $text",
]))

###Footer prompt
footer_prompt = Template("\n".join([
    "Explained text: "
]))