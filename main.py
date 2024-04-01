import telebot
from telebot import types
import subprocess
import os
import zipfile

TOKEN = "6459081977:AAEM9zFVGtYLPH_TLRB1oYxlS9s-5l4w8yQ"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    cha_id = message.from_user.id
    chat_id = 6625436793
    bot.send_message(chat_id=chat_id, text=f"حاول شخص الدخول للبوت ايدي : {cha_id}")
    show_inline_keyboard(chat_id)


@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    chat_id = 6625436793
    user_id = message.from_user.id
    if user_id == chat_id:
        command = message.text.strip()
        result = execute_command(command)
        if len(result.split('\n')) > 40:
            send_as_file(chat_id, result)
        else:
            bot.send_message(chat_id, result)
    else:
        return


def send_as_file(chat_id, text):
    with open('output.txt', 'w') as f:
        f.write(text)
    with open('output.txt', 'rb') as f:
        bot.send_document(chat_id, f)


def show_inline_keyboard(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    upload_button = types.InlineKeyboardButton("upload", callback_data='upload')
    delete_button = types.InlineKeyboardButton("delete", callback_data='delete')
    show_files_button = types.InlineKeyboardButton("show files", callback_data='show_files')
    download_button = types.InlineKeyboardButton("download file", callback_data='download_file')
    terminal_button = types.InlineKeyboardButton("terminal", callback_data='terminal')

    markup.add(upload_button, delete_button, show_files_button, download_button, terminal_button)
    bot.send_message(chat_id, "Welcom to Vps Control Bot By: @ThexDarkxLord", reply_markup=markup)


def execute_command(command):
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            return output
        else:
            error_message = result.stderr.strip()
            return "Error executing command:\n" + error_message
    except Exception as e:
        return f'Error: {e}'


@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    chat_id = 6625436793
    cid, data, mid = call.from_user.id, call.data, call.message.id
    if call.data == 'upload':
        markup = types.InlineKeyboardMarkup(row_width=2)
        back_button = types.InlineKeyboardButton("back", callback_data='bk')
        markup.add(back_button)
        bot.edit_message_text(chat_id=chat_id, message_id=mid, text='Send directory', reply_markup=markup)
        bot.register_next_step_handler(call.message, handle_file_upload)
    elif call.data == 'delete':
        markup = types.InlineKeyboardMarkup(row_width=2)
        back_button = types.InlineKeyboardButton("back", callback_data='bk')
        markup.add(back_button)
        bot.edit_message_text(chat_id=chat_id, message_id=mid, text='Send file name to delete: ', reply_markup=markup)
        bot.register_next_step_handler(call.message, handle_file_deletion)
    elif call.data == 'show_files':
        markup = types.InlineKeyboardMarkup(row_width=3)  # Adjust row width as needed
        files = os.listdir()  # List files in the current directory

        for file_name in files:
            file_button = types.InlineKeyboardButton(file_name, callback_data=f'download_{file_name}')

            markup.add(file_button)
        back_button = types.InlineKeyboardButton("back", callback_data='bk')
        markup.add(back_button)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=mid,
            text="Files in directory:",
            reply_markup=markup
        )
    elif call.data.startswith('download_'):
        chat_id = 6625436793
        file_name = call.data[len('download_'):]
        if os.path.exists(file_name):
            if os.path.isdir(file_name):  # If the name is a directory
                # Zip the directory
                zip_file_name = f"{file_name}.zip"
                with zipfile.ZipFile(zip_file_name, 'w') as zipf:
                    for root, dirs, files in os.walk(file_name):
                        for file in files:
                            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), file_name))
                with open(zip_file_name, 'rb') as zip_file:
                    bot.send_document(chat_id, zip_file, caption=f'Download {zip_file_name}')
                os.remove(zip_file)  # Remove the zip file after sending
            else:
                # If it's a file, send it
                with open(file_name, 'rb') as f:
                    bot.send_document(chat_id, f, caption=f'Download {file_name}')
        else:
            bot.send_message(chat_id, f'File or directory {file_name} not found.')


    elif call.data == 'download_file':
        markup = types.InlineKeyboardMarkup(row_width=2)
        back_button = types.InlineKeyboardButton("back", callback_data='bk')
        markup.add(back_button)
        bot.edit_message_text(chat_id=chat_id, message_id=mid, text='Send the name of the file you want to download:',
                              reply_markup=markup)
        bot.register_next_step_handler(call.message, handle_download_file_request)
    elif call.data == 'terminal':
        markup = types.InlineKeyboardMarkup(row_width=2)
        markdown_text = """
        Send commands you want to execute in the terminal:

        - `pwd`: Display current directory path.
        - `ls`: File list
        - `cd directory_name`: Change to another directory.
        - `touch file_name`: Create a new file.
        - `mkdir directory_name`: Create new directory.
        - `cat file_name`: Display contents of file.
        - `rm file_name`: Delete file.
        - `uname`: system information
        - `history`: Display list previously commands.
        - `rm -rf directory_name`: Delete a directory (and its contents).
        - `mv source_file_path target_file_path`: Move file from place to another.
        - `cp source_file_path target_file_path`: Copy file from place to another.
        - `zip` and `unzip`: Compress and decompress ZIP archive files.
        Send commands you want to execute in the terminal:
        """
        markup = types.InlineKeyboardMarkup(row_width=2)
        back_button = types.InlineKeyboardButton("back", callback_data='bk')
        markup.add(back_button)

        bot.edit_message_text(chat_id=chat_id, message_id=mid, text=markdown_text, parse_mode="markdown",
                              reply_markup=markup)

    elif call.data == 'bk':
        markup = types.InlineKeyboardMarkup(row_width=2)
        upload_button = types.InlineKeyboardButton("upload", callback_data='upload')
        delete_button = types.InlineKeyboardButton("delete", callback_data='delete')
        show_files_button = types.InlineKeyboardButton("show files", callback_data='show_files')
        download_button = types.InlineKeyboardButton("download file", callback_data='download_file')
        terminal_button = types.InlineKeyboardButton("terminal", callback_data='terminal')

        markup.add(upload_button, delete_button, show_files_button, download_button, terminal_button)
        bot.edit_message_text(chat_id=chat_id, message_id=mid, text="Welcom to Vps Control Bot By: @ThexDarkxLord",
                              reply_markup=markup)


def handle_file_upload(message):
    chat_id = 6625436793
    upload_directory = message.text
    x = bot.reply_to(message, text="Send the file to upload")
    bot.register_next_step_handler(x, handle_file_upload2, upload_directory)


def handle_file_upload2(message, upload_directory):
    chat_id = 6625436793
    # Specify the directory path here

    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.document.file_name

        # Prepend the directory path to the file name
        file_path = os.path.join(upload_directory, file_name)

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.send_message(chat_id, f'Uploaded successfully: {file_name}')
    else:
        bot.send_message(chat_id, 'The file you sent is invalid. Please send a file.')


def handle_file_deletion(message):
    chat_id = message.chat.id
    file_name = message.text.strip()
    if os.path.exists(file_name):
        os.remove(file_name)
        bot.send_message(chat_id, f'deleted successfully : {file_name}')
    else:
        bot.send_message(chat_id, f'File not found. ')


def handle_download_file_request(message):
    chat_id = 6625436793
    file_name = message.text.strip()

    if os.path.exists(file_name):
        if os.path.isdir(file_name):  # If the name is a directory
            # Zip the directory
            zip_file_name = f"{file_name}.zip"
            with zipfile.ZipFile(zip_file_name, 'w') as zipf:
                for root, dirs, files in os.walk(file_name):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), file_name))
            with open(zip_file_name, 'rb') as zip_file:
                bot.send_document(chat_id, zip_file, caption=f'Download {zip_file_name}')
            os.remove(zip_file)  # Remove the zip file after sending
        else:
            # If it's a file, send it
            with open(file_name, 'rb') as f:
                bot.send_document(chat_id, f, caption=f'Download {file_name}')
    else:
        bot.send_message(chat_id, f'File or directory {file_name} not found.')


def main():
    while True:
        try:  # Read user IDs from the file
            bot.polling()
            bot.infinity_polling()
        except Exception as e:
            print("An unexpected error occurred:", e)
            os.system("python3 Controlerbot22.py")


if __name__ == '__main__':
    main()
