// Enhanced JavaScript for CTI Protexion
document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            navToggle.classList.toggle('active');

            // Update ARIA attributes
            const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
            navToggle.setAttribute('aria-expanded', !isExpanded);
        });
    }

    // Enhanced navbar scroll effect
    let lastScrollY = window.scrollY;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        lastScrollY = currentScrollY;
    });

    // Animated counter for hero stats
    function animateCounter(element, target, duration = 2000) {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current).toLocaleString();
        }, 16);
    }

    // Initialize counters when they come into view
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const target = parseInt(entry.target.dataset.target) || 0;
                entry.target.innerHTML = ''; // Remove loading spinner
                animateCounter(entry.target, target);
                entry.target.dataset.animated = 'true';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.stat-number[data-target]').forEach(el => {
        observer.observe(el);
    });

    // Code tabs functionality
    const codeTabs = document.querySelectorAll('.code-tab');
    const codeBlocks = document.querySelectorAll('.code-block');

    codeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const lang = tab.dataset.lang;

            // Remove active class from all tabs and blocks
            codeTabs.forEach(t => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            codeBlocks.forEach(b => b.classList.remove('active'));

            // Add active class to clicked tab and corresponding block
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');
            document.querySelector(`.code-block[data-lang="${lang}"]`).classList.add('active');
        });
    });

    // Enhanced API functions
    async function updateStats() {
        try {
            const response = await fetch('/status');
            const data = await response.json();

            // Update status indicator
            const statusIndicator = document.querySelector('.status-indicator');
            if (statusIndicator && data.status === 'online') {
                statusIndicator.style.background = 'var(--success)';
            }

            // Update counters if not already animated
            if (data.ip_count !== undefined) {
                const ipCountEl = document.querySelector('[data-target]');
                if (ipCountEl && !ipCountEl.dataset.animated) {
                    ipCountEl.dataset.target = data.ip_count;
                }
            }

        } catch (error) {
            console.log('Erro ao atualizar estatísticas:', error);
            showNotification('Erro ao carregar estatísticas', 'error');
        }
    }

    // Load dynamic URL list
    async function loadUrlList() {
        try {
            const response = await fetch('/honeypot-urls.txt');
            const text = await response.text();
            const urls = text.split('\n').filter(line => line && !line.startsWith('#'));

            const listEl = document.getElementById('urlList');
            const countEl = document.querySelector('.url-count');

            if (listEl) {
                listEl.innerHTML = '';

                if (urls.length === 0) {
                    const li = document.createElement('li');
                    li.textContent = 'Nenhuma URL maliciosa detectada no momento';
                    li.style.fontStyle = 'italic';
                    li.style.color = 'var(--gray-500)';
                    listEl.appendChild(li);
                } else {
                    // Show only first 50 URLs to avoid performance issues
                    const displayUrls = urls.slice(0, 50);

                    displayUrls.forEach((url, index) => {
                        const li = document.createElement('li');
                        li.textContent = url;
                        li.style.animationDelay = `${index * 50}ms`;
                        li.classList.add('fade-in-up');
                        listEl.appendChild(li);
                    });

                    if (urls.length > 50) {
                        const li = document.createElement('li');
                        li.innerHTML = `<em>... e mais ${urls.length - 50} URLs (baixe a lista completa)</em>`;
                        li.style.color = 'var(--gray-500)';
                        li.style.fontStyle = 'italic';
                        listEl.appendChild(li);
                    }
                }
            }

            if (countEl) {
                countEl.textContent = `${urls.length} URLs detectadas`;
            }

        } catch (error) {
            console.log('Erro ao carregar URLs:', error);
            const listEl = document.getElementById('urlList');
            if (listEl) {
                listEl.innerHTML = '<li style="color: var(--error);">Erro ao carregar URLs maliciosas</li>';
            }
        }
    }

    // Copy code functionality
    window.copyCode = async function(button) {
        const codeBlock = button.nextElementSibling.querySelector('code');
        const text = codeBlock.textContent;

        try {
            await navigator.clipboard.writeText(text);

            // Visual feedback
            const originalText = button.textContent;
            button.textContent = 'Copiado!';
            button.style.background = 'var(--success)';
            button.style.color = 'var(--dark)';

            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '';
                button.style.color = '';
            }, 2000);

            showNotification('Código copiado com sucesso!', 'success');
        } catch (err) {
            showNotification('Erro ao copiar código', 'error');
        }
    };

    // Notification system
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Animate out and remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    };

    // Initialize data loading
    updateStats();
    loadUrlList();

    // Update stats every 30 seconds
    setInterval(updateStats, 30000);

    // Update URLs every 5 minutes
    setInterval(loadUrlList, 300000);

    // Add fade-in animation to sections
    const sections = document.querySelectorAll('.section');
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, { threshold: 0.1 });

    sections.forEach(section => {
        sectionObserver.observe(section);
    });

    // Performance optimization: Reduce animations on low-end devices
    if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) {
        document.documentElement.style.setProperty('--transition-normal', '150ms ease');
        document.documentElement.style.setProperty('--transition-slow', '200ms ease');
    }

    // Accessibility: Respect user's motion preferences
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.documentElement.style.setProperty('--transition-fast', '0ms');
        document.documentElement.style.setProperty('--transition-normal', '0ms');
        document.documentElement.style.setProperty('--transition-slow', '0ms');
    }
});

// Global CTI API interface
window.CTIProtexion = {
    async testEndpoint(endpoint) {
        try {
            const response = await fetch(endpoint);
            const data = await response.json();
            console.log(`Dados de ${endpoint}:`, data);
            return data;
        } catch (error) {
            console.error(`Erro ao testar ${endpoint}:`, error);
            return null;
        }
    },

    async getAllNodes() {
        return await this.testEndpoint('/api/nodes');
    },

    async getRunningNodes() {
        return await this.testEndpoint('/api/nodes/running');
    },

    async getStats() {
        return await this.testEndpoint('/api/stats');
    },

    async getStatus() {
        return await this.testEndpoint('/status');
    }
};