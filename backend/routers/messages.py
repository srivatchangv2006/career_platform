from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from dependencies import get_db
from dependencies.auth import get_current_user

from models.conversation import Conversation
from models.conversation_participant import ConversationParticipant
from models.message import Message
from models.user import User
from services.public_user import get_public_user

from schemas.conversation import (
    ConversationResponse,
    ConversationSummaryResponse,
)
from schemas.message import (
    MessageCreate,
    MessageResponse,
    MessageUpdate,
)


router = APIRouter(
    prefix="/messages",
    tags=["Direct Messages"],
)


# ============================================================
# HELPERS
# ============================================================

def get_participant(
    db: Session,
    conversation_id: UUID,
    user_id: UUID,
):
    return (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id
            == conversation_id,
            ConversationParticipant.user_id
            == user_id,
        )
        .first()
    )


def get_conversation_or_404(
    db: Session,
    conversation_id: UUID,
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return build_conversation_response(
        db,
        conversation,
        current_user.id,
    )


def ensure_participant(
    db: Session,
    conversation_id: UUID,
    user_id: UUID,
):
    participant = get_participant(
        db,
        conversation_id,
        user_id,
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this conversation",
        )

    return participant


def find_existing_one_to_one_conversation(
    db: Session,
    user_a_id: UUID,
    user_b_id: UUID,
):
    conversation = (
        db.query(Conversation)
        .join(
            ConversationParticipant,
            ConversationParticipant.conversation_id
            == Conversation.id,
        )
        .filter(
            ConversationParticipant.user_id.in_(
                [user_a_id, user_b_id]
            )
        )
        .group_by(Conversation.id)
        .having(
            func.count(
                ConversationParticipant.user_id
            ) == 2
        )
        .first()
    )

    if not conversation:
        return None

    participant_ids = {
        participant.user_id
        for participant in (
            db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id
                == conversation.id
            )
            .all()
        )
    }

    if participant_ids == {
        user_a_id,
        user_b_id,
    }:
        return conversation

    return None


def build_conversation_response(
    db: Session,
    conversation: Conversation,
    current_user_id: UUID,
) -> ConversationResponse:
    participant = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id
            == conversation.id,
            ConversationParticipant.user_id
            != current_user_id,
        )
        .first()
    )

    public_user = None

    if participant:
        public_user = get_public_user(
            db,
            participant.user_id,
        )

    return ConversationResponse(
        id=conversation.id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        other_user_id=(
            participant.user_id
            if participant
            else None
        ),
        other_user_email=(
            public_user.get("email")
            if public_user
            else None
        ),
        other_user_name=(
            public_user.get("display_name")
            if public_user
            else None
        ),
        other_user_role=(
            public_user.get("role")
            if public_user
            else None
        ),
        other_user_headline=(
            public_user.get("headline")
            if public_user
            else None
        ),
        other_user_company=(
            public_user.get("company_name")
            if public_user
            else None
        ),
        other_user_avatar=(
            public_user.get(
                "profile_image_blob_path"
            )
            if public_user
            else None
        ),
    )


# ============================================================
# CREATE OR GET ONE-TO-ONE CONVERSATION
# ============================================================

@router.post(
    "/conversations/with/{user_id}",
    response_model=ConversationResponse,
)
def create_or_get_conversation(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot start a conversation with yourself",
        )

    other_user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing = find_existing_one_to_one_conversation(
        db,
        current_user.id,
        user_id,
    )

    if existing:
        return build_conversation_response(
            db,
            existing,
            current_user.id,
        )

    conversation = Conversation()

    db.add(conversation)
    db.flush()

    db.add_all(
        [
            ConversationParticipant(
                conversation_id=conversation.id,
                user_id=current_user.id,
            ),
            ConversationParticipant(
                conversation_id=conversation.id,
                user_id=user_id,
            ),
        ]
    )

    db.commit()
    db.refresh(conversation)

    return build_conversation_response(
        db,
        conversation,
        current_user.id,
    )


# ============================================================
# GET MY CONVERSATION INBOX
#
# Includes:
#   - other user
#   - last message
#   - last message time
#   - unread count
# ============================================================

@router.get(
    "/conversations",
    response_model=list[ConversationSummaryResponse],
)
def get_my_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = (
        db.query(Conversation)
        .join(
            ConversationParticipant,
            ConversationParticipant.conversation_id
            == Conversation.id,
        )
        .filter(
            ConversationParticipant.user_id
            == current_user.id
        )
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )

    results = []

    for conversation in conversations:
        other_participant = (
            db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id
                == conversation.id,
                ConversationParticipant.user_id
                != current_user.id,
            )
            .first()
        )

        if not other_participant:
            continue

        other_user = (
            db.query(User)
            .filter(
                User.id
                == other_participant.user_id
            )
            .first()
        )

        if not other_user:
            continue

        public_user = get_public_user(
            db,
            other_user.id,
        )

        last_message = (
            db.query(Message)
            .filter(
                Message.conversation_id
                == conversation.id
            )
            .order_by(
                Message.created_at.desc()
            )
            .first()
        )

        unread_count = (
            db.query(Message)
            .filter(
                Message.conversation_id
                == conversation.id,
                Message.sender_id
                != current_user.id,
                Message.is_read.is_(False),
            )
            .count()
        )

        results.append(
            ConversationSummaryResponse(
                id=conversation.id,
                other_user_id=other_user.id,

                other_user_email=(
                    other_user.email
                ),

                other_user_name=(
                    public_user.get(
                        "display_name"
                    )
                    if public_user
                    else None
                ),

                other_user_role=(
                    public_user.get(
                        "role"
                    )
                    if public_user
                    else None
                ),

                other_user_headline=(
                    public_user.get(
                        "headline"
                    )
                    if public_user
                    else None
                ),

                other_user_company=(
                    public_user.get(
                        "company_name"
                    )
                    if public_user
                    else None
                ),

                other_user_avatar=(
                    public_user.get(
                        "profile_image_blob_path"
                    )
                    if public_user
                    else None
                ),

                last_message=(
                    last_message.content
                    if last_message
                    else None
                ),

                last_message_at=(
                    last_message.created_at
                    if last_message
                    else None
                ),

                unread_count=unread_count,

                updated_at=(
                    conversation.updated_at
                ),
            )
        )

    return results


# ============================================================
# GET ONE CONVERSATION
# ============================================================

@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation_or_404(
        db,
        conversation_id,
    )

    ensure_participant(
        db,
        conversation_id,
        current_user.id,
    )

    return conversation


# ============================================================
# GET MESSAGES
# ============================================================

@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_messages(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_conversation_or_404(
        db,
        conversation_id,
    )

    ensure_participant(
        db,
        conversation_id,
        current_user.id,
    )

    return (
        db.query(Message)
        .filter(
            Message.conversation_id
            == conversation_id
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )


# ============================================================
# SEND MESSAGE
#
# New messages start as unread.
# ============================================================

@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    conversation_id: UUID,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation_or_404(
        db,
        conversation_id,
    )

    ensure_participant(
        db,
        conversation_id,
        current_user.id,
    )

    content = message_data.content.strip()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty",
        )

    message = Message(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        content=content,
        is_read=False,
    )

    db.add(message)

    conversation.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(message)

    return message


# ============================================================
# MARK CONVERSATION AS READ
#
# Marks only messages sent by the OTHER participant
# as read.
# ============================================================

@router.post(
    "/conversations/{conversation_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
)
def mark_conversation_as_read(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_conversation_or_404(
        db,
        conversation_id,
    )

    ensure_participant(
        db,
        conversation_id,
        current_user.id,
    )

    (
        db.query(Message)
        .filter(
            Message.conversation_id
            == conversation_id,
            Message.sender_id
            != current_user.id,
            Message.is_read.is_(False),
        )
        .update(
            {"is_read": True},
            synchronize_session=False,
        )
    )

    db.commit()

    return None


# ============================================================
# UPDATE OWN MESSAGE
# ============================================================

@router.put(
    "/{message_id}",
    response_model=MessageResponse,
)
def update_message(
    message_id: UUID,
    message_data: MessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = (
        db.query(Message)
        .filter(
            Message.id == message_id
        )
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    ensure_participant(
        db,
        message.conversation_id,
        current_user.id,
    )

    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own messages",
        )

    content = message_data.content.strip()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty",
        )

    message.content = content
    message.updated_at = datetime.now(
        timezone.utc
    )

    db.commit()
    db.refresh(message)

    return message


# ============================================================
# DELETE OWN MESSAGE
# ============================================================

@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_message(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = (
        db.query(Message)
        .filter(
            Message.id == message_id
        )
        .first()
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    ensure_participant(
        db,
        message.conversation_id,
        current_user.id,
    )

    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own messages",
        )

    db.delete(message)
    db.commit()

    return None
