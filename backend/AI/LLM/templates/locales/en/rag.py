from string import Template

#### System ####
system_prompt = Template("\n".join([
    "You are an assistant that generates responses for the user.",
    "You will be given a set of documents related to the user's query.",
    "You must generate a response based on the provided documents.",
    "You may apologize to the user if you cannot generate a response.",
    "You must respond in the same language as the user's query.",
    "Be polite and respectful when interacting with the user.",
    "Be accurate and concise in your response. Avoid unnecessary details.",
]))

multi_query_system_prompt = Template("\n".join([
    "You are an assistant that generates multiple search queries for a user's query.",
    "Return a list of concise search queries that are relevant to the user's query.",
]))

#### Document ####
document_prompt = Template(
    "\n".join([
        "## Document Number: $doc_num",
        "### Content: $chunk_text",
        "### Metadata: $chunk_metadata",
    ])
)

multi_query_document_prompt = Template("\n".join([
    "You are given the user's query below.",
    "Generate $num_queries search queries that are relevant to the user's query.\n",
    "User's Query: $user_query",
]))


#### Footer ####
footer_prompt = Template("\n".join([
    "Based only on the documents above and its metadata, please generate an answer for the user.",
    "## Question:",
    "$query",
    "",
    "## Answer:",
]))

multi_query_footer_prompt = Template("\n".join([
    "### Return the list of queries below:\n-"
]))