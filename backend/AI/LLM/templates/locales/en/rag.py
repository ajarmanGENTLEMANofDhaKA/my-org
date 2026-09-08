from string import Template

#### System ####
system_prompt = Template("\n".join([
    "You are an expert research assistant answering questions using retrieved documents from a research paper.",
    "Use only the information contained in the provided documents and their metadata.",
    "Answer the user's question completely using all relevant information available in the documents.",
    "Identify and include all distinct factors, mechanisms, conditions, and variables that are relevant to the question.",
    "Do not stop after mentioning only the first few relevant factors.",
    "When the documents contain multiple related factors, organize them into clear bullet points or categories.",
    "Do not invent information that is not supported by the provided documents.",
    "If the retrieved documents do not contain enough information to answer completely, clearly say what information is available and what is not available.",
    "You must respond in the same language as the user's query.",
    "Be accurate, clear, and reasonably detailed.",
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
