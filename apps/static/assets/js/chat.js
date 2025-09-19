$(document).ready(function() {
    const messageForm = $('#message-form');
    const messageInput = $('#message-input');
    const messageBox = $('#message-box');
    const loadingSpinner = $('#loading-spinner');
    const newChatForm = $('#new-chat-form');
    const chatNameInput = $('#chat-name-input');

    // Function to create message element
    function createMessageElement(message) {
        const messageDiv = $('<div>').addClass('row mb-4');
        
        // Add justify-content class based on message type
        if (message.system_message) {
            messageDiv.addClass('justify-content-end');
        } else {
            messageDiv.addClass('justify-content-start');
        }
        
        const colDiv = $('<div>').addClass('col-auto');
        const cardDiv = $('<div>').addClass('card');
        
        if (message.system_message) {
            cardDiv.addClass('bg-gray-100');
        }
        
        const cardBodyDiv = $('<div>').addClass('card-body py-2 px-3');
        
        // Add message content
        const messageP = $('<p>').addClass('mb-1');
        if (message.sql) {
            const pre = $('<pre>').addClass('mb-0');
            const code = $('<code>').addClass('language-sql').text(message.message);
            pre.append(code);
            messageP.append(pre);
            
            // Add data table if results are available
            if (message.head_data) {
                const data = typeof message.head_data === 'string' ? JSON.parse(message.head_data) : message.head_data;
                if (data && data.length > 0) {
                    const tableDiv = $('<div>').addClass('table-responsive mt-3');
                    const table = $('<table>').addClass('table table-sm table-striped');
                    
                    // Add headers
                    const thead = $('<thead>');
                    const headerRow = $('<tr>');
                    Object.keys(data[0]).forEach(key => {
                        headerRow.append($('<th>').text(key));
                    });
                    thead.append(headerRow);
                    table.append(thead);
                    
                    // Add data rows
                    const tbody = $('<tbody>');
                    data.forEach(row => {
                        const tr = $('<tr>');
                        Object.values(row).forEach(value => {
                            tr.append($('<td>').text(value !== null ? value : ''));
                        });
                        tbody.append(tr);
                    });
                    table.append(tbody);
                    
                    tableDiv.append(table);
                    messageP.append(tableDiv);
                }
            }
        } else {
            messageP.text(message.message);
        }
        cardBodyDiv.append(messageP);
        
        // Add timestamp and buttons
        const metaDiv = $('<div>').addClass('d-flex align-items-center text-sm opacity-6');
        const timestamp = $('<small>').addClass('me-3').text(message.timestamp);
        metaDiv.append(timestamp);
        
        // Only show Run button for SQL messages without data
        if (message.sql && !message.head_data) {
            const runButton = $('<button>')
                .addClass('btn btn-sm btn-outline-primary mb-0 run-sql-btn')
                .attr('data-sql', message.sql)
                .html('<i class="fas fa-play"></i> Run');
            metaDiv.append(runButton);
        }
        
        // Only show Visualize button for messages with data
        if (message.head_data) {
            const vizButton = $('<a>')
                .addClass('btn btn-sm btn-outline-primary mb-0')
                .attr('href', `/visualization?message_id=${message.id}`)
                .html('<i class="fas fa-chart-bar"></i> Visualize Data');
            metaDiv.append(vizButton);
        }
        
        cardBodyDiv.append(metaDiv);
        cardDiv.append(cardBodyDiv);
        colDiv.append(cardDiv);
        messageDiv.append(colDiv);
        
        return messageDiv;
    }
    
    // Function to append messages to the message box
    function appendMessages(messages) {
        messages.forEach(message => {
            const messageElement = createMessageElement(message);
            $('#message-box').append(messageElement);
        });
        
        // Scroll to bottom
        const messageBox = document.getElementById('message-box');
        messageBox.scrollTop = messageBox.scrollHeight;
        
        // Initialize syntax highlighting
        if (typeof hljs !== 'undefined') {
            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
            });
        }
    }

    // Function to add a message to the chat box
    function addMessage(message, isSystem = false) {
        let messageContent;
        
        // Check if message is a SQL query
        if (isSystem && (message.trim().toUpperCase().startsWith('SELECT') || 
                        message.trim().toUpperCase().startsWith('WITH'))) {
            const chatId = new URLSearchParams(window.location.search).get('chat_id');
            messageContent = `
                <div class="sql-message" data-message-id="${messageBox.children().length + 1}">
                    <pre class="language-sql"><code class="language-sql">${message}</code></pre>
                    <button class="btn btn-primary run-sql-btn" data-query="${encodeURIComponent(message)}" data-chat-id="${chatId}">
                        <i class="fas fa-play"></i> Run Query
                    </button>
                    <div class="sql-results" style="display: none;"></div>
                </div>
            `;
        } else {
            messageContent = `<p class="mb-1">${message}</p>`;
        }
        
        const messageHtml = `
            <div class="row justify-content-${isSystem ? 'end' : 'start'} mb-4">
                <div class="col-auto">
                    <div class="card ${isSystem ? 'bg-gray-100' : ''}" style="max-width: 80vw;">
                        <div class="card-body py-2 px-3">
                            ${messageContent}
                            <div class="d-flex align-items-center text-sm opacity-6">
                                <small>Just now</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        messageBox.append(messageHtml);
        
        // Initialize Prism.js syntax highlighting for new SQL code blocks
        if (isSystem && message.trim().toUpperCase().startsWith('SELECT')) {
            Prism.highlightAll();
        }
        
        messageBox.scrollTop(messageBox[0].scrollHeight);
    }

    // Function to create table from SQL results
    function createTable(columns, results) {
        let table = '<div class="table-responsive"><table class="table table-striped">';
        
        // Add header
        table += '<thead><tr>';
        columns.forEach(col => {
            table += `<th>${col}</th>`;
        });
        table += '</tr></thead>';
        
        // Add body
        table += '<tbody>';
        results.forEach(row => {
            table += '<tr>';
            columns.forEach(col => {
                table += `<td>${row[col] !== null ? row[col] : ''}</td>`;
            });
            table += '</tr>';
        });
        table += '</tbody></table></div>';
        
        // Add visualization button
        table += `
            <div class="mt-3">
                <button class="btn btn-success visualize-btn">
                    <i class="fas fa-chart-bar"></i> Visualize Data
                </button>
            </div>
        `;
        
        return table;
    }

    // Handle SQL execution
    $(document).on('click', '.run-sql-btn', function() {
        const button = $(this);
        const sql = button.attr('data-sql');
        const chatId = new URLSearchParams(window.location.search).get('chat_id');
        
        // Disable button and show loading
        button.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Running...');
        
        // Execute SQL
        $.ajax({
            url: '/execute-sql/',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            data: JSON.stringify({
                sql_query: sql,
                chat_id: chatId
            }),
            success: function(response) {
                // Create result message element
                const resultMessage = {
                    id: response.message_id,
                    message: sql,
                    sql: sql,
                    head_data: response.results,
                    timestamp: new Date().toLocaleString(),
                    system_message: true
                };
                
                // Replace the current message element
                button.closest('.row').replaceWith(createMessageElement(resultMessage));
                
                // Initialize syntax highlighting
                if (typeof hljs !== 'undefined') {
                    document.querySelectorAll('pre code').forEach((block) => {
                        hljs.highlightBlock(block);
                    });
                }
            },
            error: function(xhr) {
                // Re-enable button
                button.prop('disabled', false).html('<i class="fas fa-play"></i> Run');
                
                // Show error
                const error = xhr.responseJSON?.error || 'Failed to execute SQL';
                alert('Error: ' + error);
            }
        });
    });

    // Handle visualization
    $(document).on('click', '.visualize-btn', function() {
        const messageId = $(this).data('message-id');
        // Redirect to visualization page with absolute path
        window.location.href = `/visualization?message_id=${messageId}`;
    });

    // Handle message form submission
    messageForm.on('submit', function(e) {
        e.preventDefault();
        const message = messageInput.val().trim();
        if (!message) return;

        // Get current chat ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        const chatId = urlParams.get('chat_id');
        const userId = $('[name=user_id]').val();

        // Clear input and show loading spinner
        messageInput.val('');
        loadingSpinner.show();

        // Send message to backend
        $.ajax({
            url: '/new-message/',
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            },
            data: {
                message: message,
                chat_id: chatId,
                user_id: userId,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                // Hide loading spinner
                loadingSpinner.hide();
                
                if (response.error) {
                    console.error('Server error:', response.error);
                    alert('Error: ' + response.error);
                    return;
                }
                
                if (response.success && response.messages) {
                    response.messages.forEach(message => {
                        const messageElement = createMessageElement(message);
                        $('#message-box').append(messageElement);
                    });
                    
                    // Scroll to bottom
                    const messageBox = document.getElementById('message-box');
                    messageBox.scrollTop = messageBox.scrollHeight;
                    
                    // Initialize syntax highlighting
                    if (typeof hljs !== 'undefined') {
                        document.querySelectorAll('pre code').forEach((block) => {
                            hljs.highlightBlock(block);
                        });
                    }
                } else {
                    console.error('Invalid response format:', response);
                    alert('Error: Received invalid response from server');
                }
            },
            error: function(xhr, status, error) {
                // Hide loading spinner
                loadingSpinner.hide();
                
                console.error('Ajax error:', status, error);
                alert('Error: ' + (xhr.responseJSON?.error || 'Failed to send message'));
            }
        });
    });

    // Handle new chat creation
    $('#new-chat-form').on('submit', function(e) {
        e.preventDefault();
        
        const formData = {
            name: 'New Chat',
            user_id: $('input[name="user_id"]').val(),
            connection_id: $('input[name="connection_id"]').val(),
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        };
        
        console.log('Creating new chat with data:', formData);
        
        $.ajax({
            url: '/new_chat',
            method: 'POST',
            data: formData,
            success: function(response) {
                console.log('New chat created:', response);
                // Redirect to the new chat
                window.location.href = `/chat/${response.connection_id}/?chat_id=${response.chat_id}`;
            },
            error: function(xhr, status, error) {
                console.error('Error creating chat:', error);
                alert('Failed to create new chat. Please try again.');
            }
        });
    });

    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle chat deletion
    $('.chat-delete').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (!confirm('Are you sure you want to delete this chat?')) return;
        
        const chatId = $(this).data('chat-id');
        
        $.ajax({
            url: '/delete-chat',
            method: 'POST',
            data: {
                chat_id: chatId,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function() {
                // Remove the chat from the list and redirect if it's the current chat
                const urlParams = new URLSearchParams(window.location.search);
                const currentChatId = urlParams.get('chat_id');
                
                if (chatId === currentChatId) {
                    // Redirect to the first available chat or the chat page
                    const firstChat = $('.chat').first();
                    if (firstChat.length) {
                        const newChatId = firstChat.find('.chat-delete').data('chat-id');
                        window.location.href = `?chat_id=${newChatId}`;
                    } else {
                        window.location.href = '/chat';
                    }
                } else {
                    // Just remove the chat from the list
                    $(`.chat-delete[data-chat-id="${chatId}"]`).closest('.chat').remove();
                }
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
                alert('Failed to delete chat. Please try again.');
            }
        });
    });

    // Handle chat switching
    $(document).on('click', '.chat-link', function(e) {
        e.preventDefault();
        const chatUrl = $(this).attr('href');
        const chatId = new URLSearchParams(chatUrl.split('?')[1]).get('chat_id');
        
        // Update URL without full page reload
        window.history.pushState({}, '', chatUrl);
        
        // Show loading state
        $('#message-box').html('<div class="text-center p-4"><div class="spinner-border" role="status"></div></div>');
        
        // Load messages via AJAX
        $.get('/get_chat_messages', { chat_id: chatId })
            .done(function(response) {
                // Clear existing messages
                messageBox.empty();
                
                // Add each message
                appendMessages(response.messages);
                
                // Update active chat in sidebar
                $('.chat-link').removeClass('active');
                $(`[href="${chatUrl}"]`).addClass('active');
                
                // Scroll to bottom
                messageBox.scrollTop(messageBox[0].scrollHeight);
            })
            .fail(function(xhr, status, error) {
                console.error('Error loading messages:', error);
                messageBox.html('<div class="alert alert-danger">Failed to load messages. Please refresh the page.</div>');
            });
    });

    // Chat name editing
    $(document).on('click', '.edit-chat-name', function(e) {
        e.preventDefault();
        e.stopPropagation();
        const chatId = $(this).data('chat-id');
        const chatNameElement = $(`.chat-name[data-chat-id="${chatId}"]`);
        const chatNameForm = $(`.chat-name-form[data-chat-id="${chatId}"]`);
        const chatNameInput = chatNameForm.find('input');
        
        // Set input value to current name
        chatNameInput.val(chatNameElement.text().trim());
        
        // Show form, hide name
        chatNameElement.hide();
        chatNameForm.show();
        chatNameInput.focus();
    });

    $(document).on('submit', '.chat-name-form', function(e) {
        e.preventDefault();
        const form = $(this);
        const chatId = form.data('chat-id');
        const chatNameElement = $(`.chat-name[data-chat-id="${chatId}"]`);
        const newName = form.find('input').val().trim();
        
        if (!newName) {
            form.hide();
            chatNameElement.show();
            return;
        }
        
        $.ajax({
            url: '/update-chat-name',
            method: 'POST',
            data: {
                chat_id: chatId,
                name: newName,
                csrfmiddlewaretoken: getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    chatNameElement.text(newName).show();
                    form.hide();
                } else {
                    alert(response.error || 'Failed to update chat name');
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Failed to update chat name';
                alert('Error: ' + error);
                form.hide();
                chatNameElement.show();
            }
        });
    });

    // Hide chat name form when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.chat-name-form, .edit-chat-name').length) {
            $('.chat-name-form').hide();
            $('.chat-name').show();
        }
    });

    // Handle Enter key on chat name input
    $(document).on('keypress', '.chat-name-input', function(e) {
        if (e.which === 13) {
            $(this).closest('form').submit();
            return false;
        }
    });

    // Handle Escape key to cancel editing
    $(document).on('keydown', '.chat-name-input', function(e) {
        if (e.which === 27) {  // ESC key
            const form = $(this).closest('form');
            const chatId = form.data('chat-id');
            form.hide();
            $(`.chat-name[data-chat-id="${chatId}"]`).show();
            return false;
        }
    });
});
