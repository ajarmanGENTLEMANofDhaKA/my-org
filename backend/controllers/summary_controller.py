from .base_controller import BaseController
import aiofiles
import os
import asyncio
from utils import get_logger
logger = get_logger(__name__)
class SummaryController(BaseController):
    def __init__(self, summary_client, template_parser):
        super().__init__()

        self.summary_client = summary_client
        self.template_parser = template_parser 

    async def generate_summary(self, chunk_model, paper_id: str, paper_name: str):
        try:
            logger.info("Starting section-based summarization pipeline")

            system_prompt = self.template_parser.get("summarizer", "system_prompt")
            footer_prompt = self.template_parser.get("summarizer", "footer_prompt")

            # Map Step (summarize each section separately)
            section_summaries = []
            sections = await chunk_model.get_chunks_grouped_by_section(paper_id=paper_id)

            total_sections = len(sections)
            logger.info(f"Processing {total_sections} sections for paper {paper_name}")

            for i, (section_id, section_chunks) in enumerate(sections.items(), 1):
                try:
                    section_title = section_chunks[0].chunk_metadata.get("section_title", f"Section {section_id}")
                    logger.info(f"Processing section {i}/{total_sections}: {section_title}")

                    section_text = "\n\n".join([c.chunk_text for c in section_chunks])
                    section_prompt = self.template_parser.get(
                        "summarizer", "map_prompt", {"text": section_text}
                    )
                    full_prompt = "\n\n".join([section_prompt, footer_prompt])

                    section_summary = await self.summary_client.summarize_text(
                        user_prompt=full_prompt,
                        system_prompt=system_prompt,
                        temperature=0.2,
                    )
                    if section_summary:
                        section_summaries.append(
                            f"### {section_title}\n\n{section_summary.strip()}"
                        )
                        logger.info(f"Successfully processed section {i}/{total_sections}: {section_title}")
                    else:
                        logger.warning(f"No summary generated for section: {section_title}")

                    # Add delay between sections because of rate limits issue
                    if i < total_sections:
                        delay = 0.7  # 0.7 second delay
                        await asyncio.sleep(delay)

                except Exception as e:
                    logger.error(f"Failed to process section {section_title}: {str(e)}")
                    # Continue with other sections
                    continue

            logger.info(f"Completed map step for {len(section_summaries)} sections")

            if not section_summaries:
                logger.error(f"No section summaries were generated for paper {paper_name}")
                raise

            # Reduce Step (combine all section summaries)
            logger.info("Starting reduce step to combine section summaries")
            combined_sections_text = "\n\n".join(section_summaries)
            reduce_prompt = self.template_parser.get(
                "summarizer", "reduce_prompt", {"sections": combined_sections_text}
            )
            full_prompt = "\n\n".join([reduce_prompt, footer_prompt])

            try:
                final_summary = await self.summary_client.summarize_text(
                    user_prompt=full_prompt,
                    system_prompt=system_prompt,
                    temperature=0.2,
                )
                if not final_summary:
                    logger.error(f"Failed to generate final summary for {paper_name}")
                    raise

                logger.info(f"Successfully generated hierarchical summary for {paper_name}")
                return final_summary
                
            except Exception as e:
                logger.error(f"Failed to generate final summary for {paper_name}: {str(e)}")

                # If final summary fails, return the combined section summaries as fallback
                logger.info("Returning combined section summaries as fallback")
                return combined_sections_text

        except Exception as e:
            logger.error(f"Failed section-based summarization for {paper_name}: {e}")
            raise
                
    async def save_summary(self, summary_path, summary_content):        
        try:
            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
            async with aiofiles.open(summary_path, 'w', encoding='utf-8') as f:
                await f.write(summary_content)
                logger.info(f"Summary saved to {summary_path}")

        except Exception as e:
            logger.error(f"Error saving summary to {summary_path}: {e}")
            raise

    async def summary_path(self, project_title, summary_name):
        summary_filename = f'{summary_name}.md'
        summary_path = self.path_utils.get_summary_path(project_title, summary_filename)
        return summary_path

    async def rename_summary_file(self, project_title: str, old_name: str, new_name: str):
        try:
            old_path = self.path_utils.get_summary_path(project_title, f"{old_name}.md")
            new_path = self.path_utils.get_summary_path(project_title, f"{new_name}.md")

            # Validate file existence
            if not os.path.exists(old_path):
                logger.error(f"Cannot rename summary file: source file does not exist at {old_path}")
                raise FileNotFoundError(f"Source summary file not exist: {old_path}")

            if os.path.exists(new_path):
                logger.error(f"Cannot rename summary file: target file already exists at {new_path}")
                raise FileExistsError(f"A file with new name '{new_name}' already exists.")

            # Perform rename
            os.rename(old_path, new_path)
            logger.info(f"Summary file renamed successfully: {old_name} → {new_name}")
            
        except Exception as e:
            logger.error(f"Error renaming summary file {old_name} → {new_name}: {e}")
            raise