from string import Template

#### System ####
system_prompt = Template(
    "\n".join([
        "You are an assistant that generates concise and accurate summaries.",
        "You will be provided with  text of research paper.",
        "Your task is to summarize the content clearly, accurately and easy to understand.",
        "\n\n"
    ])
)

#### Document ####
map_prompt = Template(
    "\n".join([
        "Summarize the following section content in a concise manner",
        "If the section content is very short to summarize, return it as is.",
        "If the section contains researchers data, please restructure it in a clear format.",
        "Avoid adding any information not present in the section content.",

        "## section Content : $text",
    ])
)

reduce_prompt = Template(
    "\n".join([
        "Merge the following section summaries into a coherent paper summary.",
        "Make sure the final summary in markdown format and keep section distinctions clear.",
        "\n\n",
        "## summarized_sections: $sections"
    ])
)

#### Footer ####
footer_prompt = Template(
    "\n".join([
        "## Summary:",
    ])
)
