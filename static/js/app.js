/**
 * Emergency Medicine Case Simulator - JavaScript
 */

// Global utilities
window.EMCaseSimulator = {
    // API helper functions
    api: {
        async request(url, options = {}) {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            
            const config = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(url, config);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || `HTTP error! status: ${response.status}`);
                }
                
                return data;
            } catch (error) {
                console.error('API request failed:', error);
                throw error;
            }
        },
        
        async get(url) {
            return this.request(url, { method: 'GET' });
        },
        
        async post(url, data) {
            return this.request(url, {
                method: 'POST',
                body: JSON.stringify(data),
            });
        },

        // Streaming chat request
        async streamChat(url, data, onChunk) {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    
                    // Keep the last incomplete line in buffer
                    buffer = lines.pop() || '';
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data === '[DONE]') {
                                return;
                            }
                            try {
                                const parsed = JSON.parse(data);
                                onChunk(parsed);
                            } catch (e) {
                                console.warn('Failed to parse chunk:', data);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Stream request failed:', error);
                throw error;
            }
        }
    },
    
    // Utility functions
    utils: {
        formatTimestamp(timestamp) {
            return new Date(timestamp).toLocaleString();
        },
        
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },
        
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            }
        }
    },
    
    // UI helper functions
    ui: {
        showLoading(element, text = 'Loading...') {
            const loadingHtml = `
                <div class="flex items-center justify-center py-4">
                    <div class="flex items-center space-x-2 text-muted-foreground">
                        <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span>${text}</span>
                    </div>
                </div>
            `;
            element.innerHTML = loadingHtml;
        },
        
        showError(element, message) {
            const errorHtml = `
                <div class="rounded-lg border border-destructive/50 text-destructive p-4">
                    <div class="flex">
                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium">Error</h3>
                            <div class="mt-2 text-sm">${message}</div>
                        </div>
                    </div>
                </div>
            `;
            element.innerHTML = errorHtml;
        },
        
        showToast(message, type = 'success') {
            const toastId = 'toast-' + Date.now();
            const bgColor = type === 'success' ? 'bg-green-600' : 
                          type === 'error' ? 'bg-red-600' : 
                          type === 'warning' ? 'bg-yellow-600' : 'bg-blue-600';
            
            const toast = document.createElement('div');
            toast.id = toastId;
            toast.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-2 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full`;
            toast.textContent = message;
            
            document.body.appendChild(toast);
            
            // Animate in
            setTimeout(() => {
                toast.classList.remove('translate-x-full');
            }, 100);
            
            // Auto remove
            setTimeout(() => {
                toast.classList.add('translate-x-full');
                setTimeout(() => {
                    if (document.getElementById(toastId)) {
                        document.body.removeChild(toast);
                    }
                }, 300);
            }, 3000);
        },
        
        scrollToBottom(element) {
            element.scrollTop = element.scrollHeight;
        },
        
        focusElement(selector) {
            const element = document.querySelector(selector);
            if (element) {
                element.focus();
            }
        }
    },
    
    // Chat related functions
    chat: {
        formatMessage(role, content, timestamp) {
            const isUser = role === 'user';
            const time = timestamp ? new Date(timestamp).toLocaleTimeString() : '';
            
            return `
                <div class="mb-4 chat-message ${isUser ? 'ml-auto max-w-[80%]' : 'mr-auto max-w-[80%]'}">
                    <div class="rounded-lg px-4 py-2 ${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'}">
                        <div class="flex items-center justify-between mb-1">
                            <div class="text-sm font-medium">${isUser ? 'You' : 'AI Physician'}</div>
                            ${time ? `<div class="text-xs opacity-75">${time}</div>` : ''}
                        </div>
                        <div class="text-sm">${this.processContent(content)}</div>
                    </div>
                </div>
            `;
        },
        
        processContent(content) {
            // Don't escape HTML first - process markdown then escape what needs escaping
            let processed = content;
            
            // Convert **bold** to HTML
            processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            // Convert *italic* to HTML  
            processed = processed.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
            
            // Convert line breaks to HTML
            processed = processed.replace(/\n/g, '<br>');
            
            // Convert bullet points (- or *) to HTML lists
            processed = processed.replace(/^(\s*[-*]\s+.+)$/gm, (match, p1) => {
                return `<li>${p1.replace(/^\s*[-*]\s+/, '')}</li>`;
            });
            
            // Wrap consecutive list items in ul tags
            processed = processed.replace(/(<li>.*<\/li>(\s*<br>\s*)?)+/g, (match) => {
                const items = match.replace(/<br>\s*/g, '').trim();
                return `<ul class="list-disc list-inside ml-4 my-2">${items}</ul>`;
            });
            
            return processed;
        },

        createStreamingMessage(role, initialContent = '') {
            const isUser = role === 'user';
            const messageDiv = document.createElement('div');
            messageDiv.className = `mb-4 chat-message ${isUser ? 'ml-auto max-w-[80%]' : 'mr-auto max-w-[80%]'}`;
            
            messageDiv.innerHTML = `
                <div class="rounded-lg px-4 py-2 ${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'}">
                    <div class="flex items-center justify-between mb-1">
                        <div class="text-sm font-medium">${isUser ? 'You' : 'AI Physician'}</div>
                        <div class="text-xs opacity-75">${new Date().toLocaleTimeString()}</div>
                    </div>
                    <div class="text-sm content">${this.processContent(initialContent)}</div>
                    <div class="typing-indicator hidden">
                        <span class="inline-block w-1 h-1 bg-current rounded-full animate-pulse"></span>
                        <span class="inline-block w-1 h-1 bg-current rounded-full animate-pulse" style="animation-delay: 0.2s"></span>
                        <span class="inline-block w-1 h-1 bg-current rounded-full animate-pulse" style="animation-delay: 0.4s"></span>
                    </div>
                </div>
            `;
            
            return messageDiv;
        },

        updateStreamingMessage(messageDiv, content) {
            const contentDiv = messageDiv.querySelector('.content');
            const typingIndicator = messageDiv.querySelector('.typing-indicator');
            
            if (contentDiv) {
                contentDiv.innerHTML = this.processContent(content);
            }
            
            if (typingIndicator) {
                typingIndicator.classList.add('hidden');
            }
        },

        showTypingIndicator(messageDiv) {
            const typingIndicator = messageDiv.querySelector('.typing-indicator');
            if (typingIndicator) {
                typingIndicator.classList.remove('hidden');
            }
        }
    },
    
    // Local storage helpers
    storage: {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (error) {
                console.warn('localStorage not available:', error);
            }
        },
        
        get(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (error) {
                console.warn('localStorage not available:', error);
                return defaultValue;
            }
        },
        
        remove(key) {
            try {
                localStorage.removeItem(key);
            } catch (error) {
                console.warn('localStorage not available:', error);
            }
        },
        
        clear() {
            try {
                localStorage.clear();
            } catch (error) {
                console.warn('localStorage not available:', error);
            }
        }
    },
    
    // Form helpers
    forms: {
        serialize(form) {
            const formData = new FormData(form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                // Handle multiple values with same name
                if (data[key]) {
                    if (Array.isArray(data[key])) {
                        data[key].push(value);
                    } else {
                        data[key] = [data[key], value];
                    }
                } else {
                    data[key] = value;
                }
            }
            
            return data;
        },
        
        validate(form) {
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('border-destructive');
                    isValid = false;
                } else {
                    input.classList.remove('border-destructive');
                }
            });
            
            return isValid;
        },
        
        reset(form) {
            form.reset();
            // Remove any error styling
            form.querySelectorAll('input, textarea, select').forEach(input => {
                input.classList.remove('border-destructive');
            });
        }
    },
    
    // Accessibility helpers
    a11y: {
        announceToScreenReader(message) {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            
            document.body.appendChild(announcement);
            
            setTimeout(() => {
                document.body.removeChild(announcement);
            }, 1000);
        },
        
        trapFocus(element) {
            const focusableElements = element.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            if (focusableElements.length === 0) return;
            
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === firstElement) {
                            lastElement.focus();
                            e.preventDefault();
                        }
                    } else {
                        if (document.activeElement === lastElement) {
                            firstElement.focus();
                            e.preventDefault();
                        }
                    }
                }
            });
            
            firstElement.focus();
        }
    }
};

// Initialize global event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape key to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('[id$="Modal"]:not(.hidden)');
            modals.forEach(modal => {
                modal.classList.add('hidden');
            });
        }
    });
    
    // Handle form validation on submit
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.hasAttribute('data-validate')) {
            if (!EMCaseSimulator.forms.validate(form)) {
                e.preventDefault();
                EMCaseSimulator.ui.showToast('Please fill in all required fields', 'error');
            }
        }
    });
    
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EMCaseSimulator;
}
