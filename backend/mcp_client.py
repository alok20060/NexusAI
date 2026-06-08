import asyncio
import os
import sys
import json
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logger = logging.getLogger("mcp_client")

# Define MCP server execution parameters
SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=[SERVER_PATH],
    env=os.environ.copy()
)

async def get_business_history(business_name: str) -> list:
    """
    Asynchronously queries the MongoDB MCP server via stdio transport to retrieve 
    historical business records for the given business_name from the businesses collection.

    Args:
        business_name (str): The name of the business to query.

    Returns:
        list: A list of dicts representing historical business records, or an empty list if not found or on error.
    """
    if not business_name:
        return []

    logger.info(f"get_business_history: Connecting to MCP server to query business: {business_name}")
    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                response = await session.call_tool(
                    "get_business_history_from_db",
                    arguments={"business_name": business_name}
                )
                
                results = []
                if response and hasattr(response, "content") and response.content:
                    for block in response.content:
                        if hasattr(block, "text") and block.text:
                            try:
                                val = json.loads(block.text)
                                if isinstance(val, list):
                                    results.extend(val)
                                else:
                                    results.append(val)
                            except json.JSONDecodeError:
                                results.append(block.text)
                return results
    except Exception as e:
        logger.error(f"Error in get_business_history: {e}", exc_info=True)
        return []

async def get_historical_loan_data(business_name: str) -> list:
    """
    Asynchronously queries the MongoDB MCP server via stdio transport to retrieve 
    historical loan records for the given business_name from the loan_history collection.

    Args:
        business_name (str): The name of the business to query.

    Returns:
        list: A list of dicts representing historical loan records, or an empty list if not found or on error.
    """
    if not business_name:
        return []

    logger.info(f"get_historical_loan_data: Connecting to MCP server to query loan history: {business_name}")
    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                response = await session.call_tool(
                    "get_historical_loan_data_from_db",
                    arguments={"business_name": business_name}
                )
                
                results = []
                if response and hasattr(response, "content") and response.content:
                    for block in response.content:
                        if hasattr(block, "text") and block.text:
                            try:
                                val = json.loads(block.text)
                                if isinstance(val, list):
                                    results.extend(val)
                                else:
                                    results.append(val)
                            except json.JSONDecodeError:
                                results.append(block.text)
                return results
    except Exception as e:
        logger.error(f"Error in get_historical_loan_data: {e}", exc_info=True)
        return []
