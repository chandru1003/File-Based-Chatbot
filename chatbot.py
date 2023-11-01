import PySimpleGUI as sg

# Define the layout for the chatbot UI
layout = [
    [sg.Text('File-Based Chatbot', font='Any 15')],
    [sg.Output(size=(80, 30), key='-OUTPUT-')],
    [sg.Input(key='-IN-', size=(45, 1), enable_events=True), sg.Button('Send')],
]

# Create the window with defined layout
window = sg.Window('File-Based Chatbot', layout)
window.set_icon('icon\icons8-chat-bot-64.ico')

# Event loop to handle interactions
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    elif event == 'Send' or (event == '-IN-' and values['-IN-'] == '\r'):
        user_input = values['-IN-'].strip()
        chatbot_response = "This is where the chatbot response would be."

        print(f'User: {user_input}')
        print(f'Chatbot: {chatbot_response}')
        window['-IN-'].update('')  # Clear the input field after processing the input

window.close()
