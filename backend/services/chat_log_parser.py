import logging
import re

logger = logging.getLogger(__name__)

from fastapi import status

from backend.exceptions import AppException, ErrorCodes


class ChatLogParser:
    """Parses raw text into structured chat logs with explicit User/AI labeling."""

    @staticmethod
    def parse(text: str | None) -> str:
        """Sanitizes chat logs by ensuring speaker labels and normalized formatting.

        Args:
            text (str | None): Raw input text.

        Returns:
            str: Sanitized text with speaker labels.
        """
        if not text:
            # STRICT ERROR HANDLING (RFC 7807) - Jan 2026 Mandate
            # Use 'EMPTY_INPUT' as defined in doc for mapping to ValidationErrorReason.emptyInput
            error_code = ErrorCodes.EMPTY_INPUT
            error_message = "ChatLogParser received empty input."
            logger.error(f"{error_code}: {error_message}")
            raise AppException(
                message=error_message,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": error_code}
            )

        # NORMALIZE LINE ENDINGS (Fix for Windows \r\n)
        text = text.replace("\r\n", "\n")

        # STRATEGY 0: Arrow Injection (Priority Fix for Hybrid PDFs)
        # Use unicode escape to avoid source encoding issues
        if "\u2192" in text:
             logger.info("Detected Arrow Injection format.")
             return ChatLogParser._parse_arrow(text)

        # DEBUG
        # print(f"DEBUG: Checking strategies. Has arrow? {'→' in text}")
        
        # STRATEGY 1: Gemini Copy-Paste (Heuristic: "Gemini Chat" header + blocks)
        if "Gemini Chat" in text[:200]:  # Check first 200 chars for header
            print("DEBUG: Strategy 1 (Gemini) selected")
            logger.info("Detected Gemini Chat format.")
            parsed = ChatLogParser._parse_gemini(text)
            if not parsed and len(text) > 100:
                logger.warning("Gemini parsing resulted in empty text. Falling back to raw.")
                # Strip header if possible, else return raw
                return text.replace("Gemini Chat", "").strip()
            return parsed

        # STRATEGY 2: ChatGPT (Heuristic: "User" / "ChatGPT" lines)
        if "ChatGPT" in text[:500] and re.search(r"^User\s*$", text, re.MULTILINE):
            print("DEBUG: Strategy 2 (ChatGPT) selected")
            logger.info("Detected ChatGPT format.")
            return ChatLogParser._parse_chatgpt(text)

        # STRATEGY 3: Claude (Heuristic: "Human:" / "Assistant:")
        if "Human:" in text and "Assistant:" in text:
             print("DEBUG: Strategy 3 (Claude) selected")
             logger.info("Detected Claude format.")
             return ChatLogParser._parse_claude(text)

        # STRATEGY 4: Visual Studio Code / Terminal Copy (Heuristic: [TIME] User:)
        if re.search(r"\[\d{2}:\d{2}\]", text):
            print("DEBUG: Strategy 4 (Timestamp) selected")
            logger.info("Detected Timestamped Chat format.")
            return ChatLogParser._parse_timestamps(text)

        # STRATEGY 5: Arrow Injection (Heuristic: "→" marking user input)
        # Use unicode escape to avoid source encoding issues
        if "\u2192" in text:
             print(f"DEBUG: Strategy 5 (Arrow) selected. Arrow count: {text.count('\u2192')}")
             logger.info("Detected Arrow Injection format.")
             return ChatLogParser._parse_arrow(text)

        # STRATEGY 6: Explicit Lines (Heuristic: Lines start with "User:" or "AI:")
        # If it's already formatted, don't mess it up.
        if re.search(r"^(User|AI):", text, re.MULTILINE):
            logger.info("Detected Pre-formatted Chat.")
            return text

        # FALLBACK: Assume raw User input and prepend label
        logger.info("Unknown chat format. Defaulting to 'User:' prefix.")
        return f"User: {text}"

    @staticmethod
    def _parse_gemini(text: str) -> str:
        """Parses Gemini copy-pastes where speaker isn't always explicit."""
        lines = text.split('\n')
        output = []
        role = "User"

        # Buffer for current speaker's text
        current_block = []

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                if current_block:
                    # Flush block
                    content = "\n".join(current_block)
                    output.append(f"{role}: {content}")
                    current_block = []
                    # Flip role on empty line (paragraph break assumption)
                    role = "AI" if role == "User" else "User"
                continue

            # Skip metadata headers explicitly
            if "Gemini Chat" in clean_line or clean_line.startswith("https://"):
                continue

            # Identify explicit roles if present
            if clean_line.startswith("User:") or clean_line.startswith("AI:"):
                # If we had a previous block, flush it
                if current_block:
                    output.append(f"{role}: {' '.join(current_block)}")
                    current_block = []
                # Trust explicit label
                output.append(clean_line)
                # Reset role heuristics
                role = "User" if clean_line.startswith("AI:") else "AI"
                continue

            current_block.append(clean_line)

        # Flush final block
        if current_block:
            output.append(f"{role}: {' '.join(current_block)}")

        result = "\n\n".join(output)
        return result

    @staticmethod
    def _parse_chatgpt(text: str) -> str:
        """Parses ChatGPT copy-pastes."""
        # ChatGPT often has:
        # User
        # content...
        # ChatGPT
        # content...

        # Naive approach: Replace standalone "User" lines with "User:" and "ChatGPT" with "AI:"

        lines = text.split('\n')
        output = []
        is_header_next = True

        for line in lines:
            clean = line.strip()
            if clean == "User":
                output.append("\nUser: ") # Prep for next line
                continue
            elif clean == "ChatGPT":
                output.append("\nAI: ") # Prep for next line
                continue
            elif clean == "You": # Sometimes "You"
                 output.append("\nUser: ")
                 continue

            # If plain text, just append
            if output and output[-1].endswith(": "):
                 output[-1] += clean
            else:
                 output.append(clean)

        return "\n".join(output).replace("\n\nUser:", "\nUser:").strip() # Cleanup

    @staticmethod
    def _parse_claude(text: str) -> str:
         # Maps Human: -> User: and Assistant: -> AI:
         text = text.replace("Human:", "User:")
         text = text.replace("Assistant:", "AI:")
         return text

    @staticmethod
    def _parse_timestamps(text: str) -> str:
        """Parses logs with [HH:MM] timestamps."""
        # Regex to find "[14:05] Name:" pattern
        # We replace it with "User:" or "AI:" based on the name.

        def replace_header(match):
            name = match.group(1).lower()
            if "gemini" in name or "ai" in name or "bot" in name:
                return "AI: "
            return "User: "

        # Pattern: [14:05] Risto: -> User:
        return re.sub(r"\[\d{2}:\d{2}\]\s(.*?):\s?", replace_header, text)

    @staticmethod
    def _parse_arrow(text: str) -> str:
        """Parses text where User input is marked by an arrow '\u2192'."""
        # Pattern:
        # AI Context...
        # \u2192 User Question...
        # AI Response (often starting with formatted list or header)
        
        parts = text.split("\u2192")
        output = []
        
        # Part 0 is usually initial AI context or Metadata (or explicit previous chat)
        if parts[0].strip():
             # Recursively parse the preamble to respect existing User/AI labels
             # parts[0] is guaranteed NOT to have the arrow, so no infinite recursion.
             preamble = ChatLogParser.parse(parts[0])
             output.append(preamble)
             
        for part in parts[1:]:
             # This part STARTS with User text.
             # but it might merge into AI text immediately if newlines are missing.
             # e.g. "mikä on... toivetila 5. Ihmiset..."
             
             # Heuristic: Find the first "ListItem" like " 5. " or "Start of new Section".
             # Regex look for: 
             # 1. Space + Digit + Dot + Space + Capital Letter (e.g. " 5. Ihmiset")
             # 2. "Analyysi" or "Tiivistelmä" (Common headers)
             
             # Try to find the split point
             match = re.search(r"(\s\d+\.\s[A-Z])|(\s(Analyysi|Tiivistelmä)\s)", part)
             if match:
                 split_index = match.start()
                 user_text = part[:split_index].strip()
                 ai_text = part[split_index:].strip()
                 
                 output.append(f"User: {user_text}")
                 output.append(f"AI: {ai_text}")
             else:
                 # No obvious split, assume all is User (or just one block)
                 output.append(f"User: {part.strip()}")
                 
        return "\n\n".join(output)
