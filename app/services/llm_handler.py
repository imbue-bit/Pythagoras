from openai import OpenAI, OpenAIError
from ..core.config import LLMSettings
from ..core.logger import log

class LLMHandler:
    def __init__(self, llm_config: LLMSettings):
        if not llm_config.api_key:
            raise ValueError("OpenAI API key is missing. Please set it in the .env file.")
        self.client = OpenAI(
            api_key=llm_config.api_key,
            base_url=llm_config.base_url,
        )
        self.model = llm_config.model
        self.temperature = llm_config.temperature
        self.timeout = llm_config.timeout
        log.info(f"LLMHandler initialized for model: {self.model}")

    def generate_sql(self, nl_query: str, schema_info: str, user_permissions: dict) -> str:
        allowed_tables_str = ", ".join(user_permissions.get('allowed_tables', []))
        if allowed_tables_str == "*":
            access_constraint = "You can access all tables."
        else:
            access_constraint = f"You can ONLY query the following tables: {allowed_tables_str}."

        system_prompt = f"""
You are an expert AI assistant that converts natural language questions into SQL queries for a {schema_info.split()[0]} database.
Your response MUST be a single, valid SQL query. Do not include any explanations, markdown formatting, or anything other than the SQL query itself.

**Security Constraints:**
{access_constraint}
If the user asks about data you cannot access, you MUST respond with the exact text: ACCESS DENIED.

**Database Schema:**
{schema_info}
"""
        log.info(f"Generating SQL for query: '{nl_query}'")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": nl_query}
                ],
                temperature=self.temperature,
                timeout=self.timeout
            )
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up potential markdown code blocks
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            log.info(f"LLM generated SQL: {sql_query}")
            return sql_query.strip()
        except OpenAIError as e:
            log.error(f"LLM API call failed: {e}")
            return f"Error: Failed to contact LLM service. {e}"
        except Exception as e:
            log.error(f"An unexpected error occurred in LLMHandler: {e}")
            return f"Error: An unexpected error occurred. {e}"
