import re
import json

def parse_whatsapp_chat(chat_content):
    """
    Parses a WhatsApp chat export text content into a structured list of messages.
    Handles standard messages, multi-line messages, and system notifications.
    """
    parsed_messages = []
    # Regex to match a standard WhatsApp message line:
    # [DD.MM.YYYY, HH:MM:SS] Sender: Message Content
    # Group 1: Date (DD.MM.YYYY)
    # Group 2: Time (HH:MM:SS)
    # Group 3: Sender Name (non-greedy match until ':')
    # Group 4: Message Content (rest of the line)
    # This pattern is robust for the common bracketed timestamp format.
    message_pattern = re.compile(r"^\[(\d{2}\.\d{2}\.\d{4}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*)$")

    current_message = None

    for line in chat_content.strip().split('\n'):
        match = message_pattern.match(line)
        if match:
            # If a new message line is found, store the previous one if it exists
            if current_message:
                parsed_messages.append(current_message)

            date_str, time_str, sender, message = match.groups()
            current_message = {
                "date": date_str,
                "time": time_str,
                "sender": sender.strip(),
                "message": message.strip(),
                "type": "chat" # Indicate it's a regular chat message
            }
        elif current_message:
            # If the line doesn't match the pattern, it might be a continuation of the previous message.
            # This is a common challenge with "real world" chat exports.
            # We append it to the last identified message's content.
            current_message["message"] += "\n" + line.strip()
        else:
            # If no current message is being built and the line doesn't match, it's a standalone system message
            # or an unparseable line at the beginning. Treat it as a system message.
            parsed_messages.append({
                "type": "system",
                "content": line.strip()
            })

    # Add the last message after the loop finishes
    if current_message:
        parsed_messages.append(current_message)

    return parsed_messages

# Simulate WhatsApp chat export content as a multi-line string.
# This content mimics a real WhatsApp chat export text file, including common variations:
# - Standard messages
# - Media omitted messages (<Medya atlandı> in Turkish, similar to <Media omitted>)
# - System messages (e.g., subject changes, encryption notices)
# - Multi-line messages (where a message spans multiple lines without a new timestamp).
whatsapp_chat_export_content = """
[01.01.2023, 10:00:01] Alice: Merhaba! Nasılsın?
[01.01.2023, 10:01:15] Bob: İyiyim, teşekkürler. Sen nasılsın?
[01.01.2023, 10:05:30] Alice: Ben de iyiyim. Bu hafta sonu ne yapıyorsun?
[01.01.2023, 10:06:05] Bob: <Medya atlandı>
[01.01.2023, 10:07:22] Alice: Yeni bir şey denemek ister misin?
[01.01.2023, 10:08:40] Bob: Bu grubun konusu "Eski Konu" olarak değiştirildi.
[01.01.2023, 10:09:10] Alice: Hmm, ilginç.
[01.01.2023, 10:10:00] Bob: Mesajlar bu gruba uçtan uca şifrelemeyle korunmaktadır.
[01.01.2023, 10:11:00] Alice: Çok satırlı bir mesaj
burada devam ediyor.
Ve hatta üçüncü bir satır.
[01.01.2023, 10:12:00] Bob: Anladım.
"""

# Parse the simulated chat content
parsed_data = parse_whatsapp_chat(whatsapp_chat_export_content)

# Print the parsed data in a human-readable JSON format.
# ensure_ascii=False allows proper display of non-ASCII characters (like Turkish).
print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
