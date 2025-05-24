# backend/app/routers/slack.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
from pydantic import BaseModel
from typing import Optional
import logging

router = APIRouter(prefix="/api/v1/slack", tags=["slack"])

logger = logging.getLogger(__name__)

class SlackMessage(BaseModel):
    text: str
    channel: Optional[str] = "#code-reviews"
    username: Optional[str] = "Pink Coded Flamingo"
    icon_emoji: Optional[str] = ":flamingo:"


@router.post("/send-message")
async def send_slack_message(message: SlackMessage):
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook:
        logger.error("SLACK_WEBHOOK_URL environment variable not set")
        raise HTTPException(
            status_code=400,
            detail="Slack integration not configured"
        )

    logger.info(f"Attempting to send Slack message: {message.text[:50]}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(slack_webhook, json={
                "text": f"🦩 Pink Coded Analysis:\n{message.text}",
                "username": "Pink Coded Flamingo",
                "icon_emoji": ":flamingo:"
            })
            
            logger.info(f"Slack API response: {response.status_code} {response.text}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.text
                )
                
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Slack integration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message to Slack: {str(e)}"
        )