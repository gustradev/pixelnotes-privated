"""
Pixel Notes Backend - Notes Routes
Handles surface notes operations (decoy app)
"""
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import uuid

from app.models import (
    NoteCreateRequest,
    NoteResponse,
    NotesListResponse,
    ErrorResponse,
)
from app.redis_client import redis_client

router = APIRouter(prefix="/notes", tags=["Notes"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "",
    response_model=NotesListResponse,
    summary="List all notes",
    description="Get list of all note IDs",
)
@limiter.limit("60/minute")
async def list_notes(request: Request):
    """
    List all note IDs.
    
    - No authentication required (surface app)
    """
    note_ids = redis_client.list_notes()
    # Extract just the IDs without the prefix
    clean_ids = [nid.replace("note:", "") for nid in note_ids]
    
    return NotesListResponse(notes=clean_ids)


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    responses={
        200: {"model": NoteResponse},
        404: {"model": ErrorResponse, "description": "Note not found"},
    },
    summary="Get a note by ID",
    description="Retrieve a specific note",
)
@limiter.limit("60/minute")
async def get_note(request: Request, note_id: str):
    """
    Get a note by ID.
    
    - No authentication required (surface app)
    """
    content = redis_client.get_note(note_id)
    
    if content is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return NoteResponse(id=note_id, content=content)


@router.post(
    "",
    response_model=NoteResponse,
    summary="Create a new note",
    description="Create a new note with optional TTL",
)
@limiter.limit("30/minute")
async def create_note(request: Request, body: NoteCreateRequest):
    """
    Create a new note.
    
    - No authentication required (surface app)
    - Optional TTL for auto-expiration
    """
    note_id = str(uuid.uuid4())[:8]
    redis_client.save_note(note_id, body.content, body.ttl)
    
    return NoteResponse(id=note_id, content=body.content)


@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    responses={
        200: {"model": NoteResponse},
        404: {"model": ErrorResponse, "description": "Note not found"},
    },
    summary="Update a note",
    description="Update an existing note",
)
@limiter.limit("30/minute")
async def update_note(request: Request, note_id: str, body: NoteCreateRequest):
    """
    Update an existing note.
    
    - No authentication required (surface app)
    """
    existing = redis_client.get_note(note_id)
    
    if existing is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    redis_client.save_note(note_id, body.content, body.ttl)
    
    return NoteResponse(id=note_id, content=body.content)


@router.delete(
    "/{note_id}",
    summary="Delete a note",
    description="Delete a note by ID",
)
@limiter.limit("30/minute")
async def delete_note(request: Request, note_id: str):
    """
    Delete a note by ID.
    
    - No authentication required (surface app)
    """
    redis_client.delete_note(note_id)
    
    return {"success": True}
