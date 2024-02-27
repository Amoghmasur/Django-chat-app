let input_message = $('#input-message')
let message_body = $('.msg_card_body')
let send_message_form = $('#send-message-form')
const USER_ID = $('#logged-in-user').val()


let loc = window.location
let wsStart = 'ws://' 

if(loc.protocol === 'https') {
    wsStart = 'wss://'
}
let endpoint = wsStart + loc.host + loc.pathname

var socket = new WebSocket(endpoint)

socket.onopen = async function(e){
    console.log('open', e)
    send_message_form.on('submit', function (e){
        e.preventDefault()
        let message = input_message.val()
        let unique_id = get_thread_or_group_unique_id();

        let data = {
            'message': message,
            'sent_by': USER_ID,
            'unique_id': unique_id 
        }
        data = JSON.stringify(data)
        socket.send(data)
        $(this)[0].reset()
    })
}

socket.onmessage = async function(e){
    console.log('message', e)
    console.log(e.data)

    let data = JSON.parse(e.data)

    let message = data['message']
    let sent_by_id = data['sent_by']
    // let thread_or_group_id = data['thread_or_group_id']
    let unique_id = data['unique_id'];
    let sent_by_username = data['sent_by_username']
    let timestamp = data['timestamp']
    newMessage(message, sent_by_id, unique_id,sent_by_username,timestamp)
}

socket.onerror = async function(e){
    console.log('error', e)
}

socket.onclose = async function(e){
    console.log('close', e)
}


function newMessage(message, sent_by_id, unique_id,sent_by_username,timestamp ) {
	if ($.trim(message) === '') {
		return false;
	}
	let message_element;
	let chat_id = 'chat_' + unique_id
	if(sent_by_id == USER_ID){
	    message_element = `
        <div class="d-flex mb-4 replied">
            <div class="message-container">
                <div class="username-replied">
                    ${sent_by_username}
                </div>
                <div class="msg_cotainer_send">
                ${message}
                    <span class="msg_time_send">${timestamp}</span>
                </div>
            </div>
        </div>
	    `
    }
	else{
	    message_element = `
        <div class="d-flex mb-4 received">
        <div class="message-block">
            <div class="username-received" >
                ${sent_by_username}
            </div>
            <div class="msg_cotainer">
                <div>
                ${message}
                    <span class="msg_time">${timestamp}</span>
                </div>
            </div>
        </div>
    </div>
        `

    }

    let message_body = $('.messages-wrapper[chat-id="' + chat_id + '"] .msg_card_body')
	message_body.append($(message_element))
    scrollToBottomOfActiveChat(true);
	input_message.val(null);
}



// function get_active_other_user_id(){
//     let other_user_id = $('.messages-wrapper.is_active_message_body').attr('other-user-id')
//     other_user_id = $.trim(other_user_id)
//     return other_user_id
// }

// function get_active_thread_or_group_id(){
//     let chat_id = $('.messages-wrapper.is_active_message_body').attr('chat-id')
//     let thread_or_group_id = chat_id.replace('chat_', '')
//     return thread_or_group_id
// }



function get_thread_or_group_unique_id() {
    let chat_id = $('.messages-wrapper.is_active_message_body').attr('chat-id')
    let thread_or_group_id = chat_id.replace('chat_', '')
    return thread_or_group_id
}



function displayStartChattingMessage() {
    $('#chat-container').hide(); 
    $('#start-chatting-message').show();
}

function showChatInterface() {
    $('#chat-container').show(); 
    $('#start-chatting-message').hide(); 
    $('#send-message-form').removeClass('hide');
}




$('.contact-li').on('click', function (){
    // message wrappers
    let chat_id = $(this).attr('chat-id')
    
    $('.messages-wrapper.is_active_message_body').removeClass('is_active_message_body')
    $('.messages-wrapper[chat-id="' + chat_id +'"]').addClass('is_active_message_body')
    scrollToBottomOfActiveChat(false);
    showChatInterface();

})



// scroll to the botttom when selected a user chat
function scrollToBottomOfActiveChat(animate = true) {
    let activeMessageWrapper = $('.messages-wrapper.is_active_message_body .msg_card_body');
    if (activeMessageWrapper.length > 0) {
        setTimeout(() => {
            if (animate) {
                activeMessageWrapper.animate({
                    scrollTop: activeMessageWrapper[0].scrollHeight
                }, 500); // animated scrolling
            } else {
                activeMessageWrapper.scrollTop(activeMessageWrapper[0].scrollHeight); // instant scrolling without animation
            }
        }, 1); // Delay of 100 milliseconds
    }
}


// csrf token retrieval function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


$(document).ready(function(){
    displayStartChattingMessage();
    scrollToBottomOfActiveChat(false);


    // auto suggestion of useers 
    $('.search').keyup(function(){
        // console.log("Searching for:", $(this).val());
        let query = $(this).val();
        if (query != '') {
            $.ajax({
                url: "/chat/search_users/",
                method: "GET",
                data: {query: query},
                success: function(data) {
                    // console.log("Received data:", data); 
                    let usersList = '<ul class="list-group">';
                    $.each(data, function(index, user){
                        usersList += `<li class="list-group-item user-suggestion " data-user-id="${user.id}">${user.username}</li>`;
                    });
                    usersList += '</ul>';
                    $('.search-results').addClass('active');
                    $('.search-results').html(usersList);
                }
            });
        } else {
            $('.search-results').removeClass('active');
            $('.search-results').html('');
        }
    });
        
        const csrftoken = getCookie('csrftoken');
        
        $(document).on('click', '.user-suggestion', function(){
            let selectedUserId = $(this).data('user-id');
            $.ajax({
                url: "/chat/create_thread/",
                method: "POST",
                data: {
                    'selected_user_id': selectedUserId,
                    'csrfmiddlewaretoken': csrftoken
                },
                success: function(response) {
                    console.log('Thread created with ID:', response.unique_id);
                    if(response.redirect_url) {
                        window.location.href = response.redirect_url;
                    }
                }
            });
        });


        ///////////////////////////////////////////////////////////
        // auto suggestion to add group members to the group 
    $('.search-add-group-members').keyup(function(){
        let query = $(this).val();
        let group_unique_id = $(this).attr('group-id');
        console.log(group_unique_id)
        if (query != '') {
            $.ajax({
                url: `/chat/search_users_add_to_group/${group_unique_id}/`,
                method: "GET",
                data: {query: query},
                success: function(data) {
                    console.log("Received data:", data); 
                    let usersList = '<ul class="list-group">';
                    $.each(data, function(index, user){
                        usersList += `<li class="list-group-item user-suggestion-add-to-group" data-user-id="${user.id}" data-group-id="${group_unique_id}">${user.username}</li>`;
                    });
                    usersList += '</ul>';
                    $('.search-results-add-to-group').addClass('active');
                    $('.search-results-add-to-group').html(usersList);
                }
            });
        } else {
            $('.search-results-add-to-group').removeClass('active');
            $('.search-results-add-to-group').html('');
        }
    });
                
        $(document).on('click', '.user-suggestion-add-to-group', function(){
            let selectedUserId = $(this).data('user-id');
            let selectedGroupUniqueId = $(this).data('group-id')
            $.ajax({
                url: "/chat/add_to_group/",
                method: "POST",
                data: {
                    'selected_user_id': selectedUserId,
                    'csrfmiddlewaretoken': csrftoken,
                    'selected_group_unique_id':selectedGroupUniqueId,
                },
                success: function(response) {
                    console.log('Member added');
                    if(response.redirect_url) {
                        window.location.href = response.redirect_url;
                    }
                }
            });
        });
});







// toggle create group
$(document).ready(function() {
    $('#create-group-plus-').click(function() {
        $('#group-creation-form').show();
    });

    $('#cancel-group-btn').click(function() {
        $('#group-creation-form').hide();
    });
});



document.getElementById('create-group-btn').addEventListener('click', function() {
    var groupName = document.getElementById('new-group-name').value;
    const csrftoken = getCookie('csrftoken');
    console.log(groupName)
    if (groupName) {
        // AJAX request to server to create group
        $.ajax({
            type: 'POST',
            url: '/chat/create_group/',
            data: {
                'group_name': groupName,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                // Handle success response
                console.log("Group created with Unique ID:", response.group_unique_id);
                if(response.redirect_url) {
                    window.location.href = response.redirect_url;
                }
            },
            error: function(error) {
                // Handle error
                console.log("Error creating group:", error);
            }
        });
        document.getElementById('group-creation-form').style.display = 'none';
    }
});
