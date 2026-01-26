/**
 * KIOSQUE DU PARC - Main JavaScript
 * Site vitrine - Vanilla JS avec API Backend
 */

(function () {
    'use strict';

    // =====================================================
    // CONFIGURATION
    // =====================================================

    const API_BASE = 'https://kiosques.onrender.com/api';

    // Category labels (mapping from backend to frontend)
    const CATEGORY_LABELS = {
        'crepes_sucrees': 'Crepe sucree',
        'crepes_salees': 'Crepe salee',
        'gaufres': 'Gaufre',
        'box': 'Box'
    };

    // Category mapping for filters (backend -> frontend filter values)
    const CATEGORY_FILTER_MAP = {
        'crepes_sucrees': 'crepe-sucree',
        'crepes_salees': 'crepe-salee',
        'gaufres': 'gaufre',
        'box': 'box'
    };

    // =====================================================
    // STATE
    // =====================================================

    let products = [];
    let currentFilter = 'all';
    let searchQuery = '';

    // =====================================================
    // DOM ELEMENTS
    // =====================================================

    const elements = {
        // Header
        header: document.getElementById('header'),
        navMenu: document.getElementById('nav-menu'),
        burgerMenu: document.getElementById('burger-menu'),
        navLinks: document.querySelectorAll('.header__nav-link'),

        // Products
        bestsellersGrid: document.getElementById('bestsellers-grid'),
        menuGrid: document.getElementById('menu-grid'),
        menuFilters: document.querySelectorAll('.menu__filter'),
        menuSearch: document.getElementById('menu-search'),
        menuEmpty: document.getElementById('menu-empty'),

        // Location
        todayLocation: document.getElementById('today-location'),
        todayHours: document.getElementById('today-hours'),
        scheduleGrid: document.getElementById('schedule-grid'),

        // Contact
        contactForm: document.getElementById('contact-form'),
        contactSubmit: document.getElementById('contact-submit'),
        formStatus: document.getElementById('form-status'),

        // Filter target buttons
        filterTargetBtns: document.querySelectorAll('[data-filter-target]')
    };

    // =====================================================
    // API FUNCTIONS
    // =====================================================

    async function fetchProducts() {
        try {
            const response = await fetch(`${API_BASE}/products`);
            if (!response.ok) throw new Error('Failed to fetch products');
            products = await response.json();
            return products;
        } catch (error) {
            console.error('Error fetching products:', error);
            return [];
        }
    }

    async function fetchBestsellers() {
        try {
            const response = await fetch(`${API_BASE}/products/best-sellers`);
            if (!response.ok) throw new Error('Failed to fetch bestsellers');
            return await response.json();
        } catch (error) {
            console.error('Error fetching bestsellers:', error);
            return [];
        }
    }

    async function fetchTodayLocation() {
        try {
            const response = await fetch(`${API_BASE}/location/today`);
            if (!response.ok) throw new Error('Failed to fetch location');
            return await response.json();
        } catch (error) {
            console.error('Error fetching location:', error);
            return null;
        }
    }

    async function fetchSchedule() {
        try {
            const response = await fetch(`${API_BASE}/schedule`);
            if (!response.ok) throw new Error('Failed to fetch schedule');
            return await response.json();
        } catch (error) {
            console.error('Error fetching schedule:', error);
            return [];
        }
    }

    // =====================================================
    // UTILITIES
    // =====================================================

    function formatPrice(price) {
        return price.toFixed(2).replace('.', ',') + ' EUR';
    }

    function getFilterCategory(backendCategory) {
        return CATEGORY_FILTER_MAP[backendCategory] || backendCategory;
    }

    // =====================================================
    // PRODUCT CARDS
    // =====================================================

    function createProductCard(product, showBestsellerTag = true) {
        const isBestseller = product.bestseller;
        const tags = product.tags || [];
        const isSweet = tags.includes('sweet');
        const isSavory = tags.includes('savory');

        const tagsHTML = [];
        if (showBestsellerTag && isBestseller) {
            tagsHTML.push('<span class="product-card__tag product-card__tag--bestseller">Best-seller</span>');
        }
        if (isSweet) {
            tagsHTML.push('<span class="product-card__tag product-card__tag--sweet">Sucre</span>');
        }
        if (isSavory) {
            tagsHTML.push('<span class="product-card__tag product-card__tag--savory">Sale</span>');
        }

        const filterCategory = getFilterCategory(product.category);
        const categoryLabel = CATEGORY_LABELS[product.category] || product.category_label || product.category;

        const card = document.createElement('article');
        card.className = 'product-card animate-on-scroll';
        card.setAttribute('data-category', filterCategory);
        card.setAttribute('data-name', product.name.toLowerCase());

        card.innerHTML = `
            <div class="product-card__image">
                <img src="${product.image}" alt="${product.alt || product.name}" loading="lazy">
                <div class="product-card__tags">
                    ${tagsHTML.join('')}
                </div>
            </div>
            <div class="product-card__content">
                <h3 class="product-card__name">${product.name}</h3>
                <p class="product-card__category">${categoryLabel}</p>
                <div class="product-card__footer">
                    <span class="product-card__price">${formatPrice(product.price)}</span>
                </div>
            </div>
        `;

        return card;
    }

    async function renderBestsellers() {
        if (!elements.bestsellersGrid) return;

        const bestsellers = await fetchBestsellers();
        elements.bestsellersGrid.innerHTML = '';

        bestsellers.forEach(product => {
            elements.bestsellersGrid.appendChild(createProductCard(product, true));
        });

        observeAnimations();
    }

    function renderMenu() {
        if (!elements.menuGrid) return;

        elements.menuGrid.innerHTML = '';
        let visibleCount = 0;

        products.forEach(product => {
            const filterCategory = getFilterCategory(product.category);
            const matchesFilter = currentFilter === 'all' || filterCategory === currentFilter;
            const matchesSearch = searchQuery === '' ||
                product.name.toLowerCase().includes(searchQuery.toLowerCase());

            if (matchesFilter && matchesSearch) {
                elements.menuGrid.appendChild(createProductCard(product, true));
                visibleCount++;
            }
        });

        // Show/hide empty message
        if (elements.menuEmpty) {
            elements.menuEmpty.hidden = visibleCount > 0;
        }

        // Trigger scroll animations for new cards
        observeAnimations();
    }

    // =====================================================
    // LOCATION & SCHEDULE
    // =====================================================

    async function renderLocation() {
        const location = await fetchTodayLocation();

        if (location) {
            if (elements.todayLocation) {
                elements.todayLocation.textContent = location.place || 'Non defini';
            }
            if (elements.todayHours) {
                elements.todayHours.textContent = location.hours || '';
            }
            // Display daily message if exists
            if (location.message && elements.todayMessage) {
                elements.todayMessage.textContent = location.message;
                elements.todayMessage.hidden = false;
            }
        }
    }

    async function renderSchedule() {
        if (!elements.scheduleGrid) return;

        const schedule = await fetchSchedule();
        elements.scheduleGrid.innerHTML = '';

        // Schedule is already sorted by day_index from API
        schedule.forEach(entry => {
            const card = document.createElement('div');
            card.className = `location__card${entry.is_weekend ? ' location__card--highlight' : ''}`;

            card.innerHTML = `
                <div class="location__day">${entry.day}</div>
                <div class="location__place">${entry.place}</div>
                <div class="location__hours">${entry.hours}</div>
            `;

            elements.scheduleGrid.appendChild(card);
        });
    }

    // =====================================================
    // NAVIGATION
    // =====================================================

    function initNavigation() {
        // Burger menu toggle
        elements.burgerMenu?.addEventListener('click', () => {
            const isActive = elements.navMenu?.classList.toggle('active');
            elements.burgerMenu?.classList.toggle('active');
            elements.burgerMenu?.setAttribute('aria-expanded', isActive ? 'true' : 'false');
        });

        // Close menu on link click (mobile)
        elements.navLinks.forEach(link => {
            link.addEventListener('click', () => {
                elements.navMenu?.classList.remove('active');
                elements.burgerMenu?.classList.remove('active');
                elements.burgerMenu?.setAttribute('aria-expanded', 'false');
            });
        });

        // Active link on scroll
        const sections = document.querySelectorAll('section[id]');
        const observerOptions = {
            rootMargin: '-50% 0px -50% 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    updateActiveNavLink(id);
                }
            });
        }, observerOptions);

        sections.forEach(section => observer.observe(section));
    }

    function updateActiveNavLink(sectionId) {
        elements.navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === `#${sectionId}`) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // =====================================================
    // MENU FILTERS & SEARCH
    // =====================================================

    function initMenuControls() {
        // Filter buttons
        elements.menuFilters.forEach(btn => {
            btn.addEventListener('click', () => {
                currentFilter = btn.dataset.filter;

                // Update active state
                elements.menuFilters.forEach(b => {
                    b.classList.remove('active');
                    b.setAttribute('aria-selected', 'false');
                });
                btn.classList.add('active');
                btn.setAttribute('aria-selected', 'true');

                renderMenu();
            });
        });

        // Search input
        elements.menuSearch?.addEventListener('input', (e) => {
            searchQuery = e.target.value;
            renderMenu();
        });

        // Filter target buttons (from category sections)
        elements.filterTargetBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const targetFilter = btn.dataset.filterTarget;

                // Find and click the corresponding filter button
                elements.menuFilters.forEach(filterBtn => {
                    if (filterBtn.dataset.filter === targetFilter) {
                        filterBtn.click();
                    }
                });

                // Scroll to menu section
                document.getElementById('menu')?.scrollIntoView({ behavior: 'smooth' });
            });
        });
    }

    // =====================================================
    // SCROLL ANIMATIONS
    // =====================================================

    function observeAnimations() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll:not(.visible)');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animatedElements.forEach(el => observer.observe(el));
    }

    // =====================================================
    // CAROUSEL NAVIGATION
    // =====================================================

    function initCarousels() {
        const carousels = document.querySelectorAll('[data-carousel]');

        carousels.forEach(carousel => {
            const track = carousel.querySelector('.carousel__track');
            const prevBtn = carousel.querySelector('[data-carousel-prev]');
            const nextBtn = carousel.querySelector('[data-carousel-next]');

            if (!track || !prevBtn || !nextBtn) return;

            const scrollAmount = 300;

            // Update button states based on scroll position
            function updateButtons() {
                const { scrollLeft, scrollWidth, clientWidth } = track;
                prevBtn.disabled = scrollLeft <= 0;
                nextBtn.disabled = scrollLeft >= scrollWidth - clientWidth - 10;
            }

            // Scroll handlers
            prevBtn.addEventListener('click', () => {
                track.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            });

            nextBtn.addEventListener('click', () => {
                track.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            });

            // Update buttons on scroll
            track.addEventListener('scroll', updateButtons, { passive: true });

            // Initial state
            updateButtons();

            // Update on window resize
            window.addEventListener('resize', updateButtons, { passive: true });

            // MutationObserver to update buttons when content changes
            const observer = new MutationObserver(() => {
                setTimeout(updateButtons, 100);
            });

            const grid = track.querySelector('.bestsellers__grid, .menu__grid');
            if (grid) {
                observer.observe(grid, { childList: true });
            }
        });
    }

    // =====================================================
    // HEADER SCROLL EFFECT
    // =====================================================

    function initHeaderScroll() {
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;

            if (currentScroll > 100) {
                elements.header?.classList.add('scrolled');
            } else {
                elements.header?.classList.remove('scrolled');
            }
        }, { passive: true });
    }

    // =====================================================
    // CONTACT FORM
    // =====================================================

    function showFormStatus(type, message) {
        if (!elements.formStatus) return;

        elements.formStatus.hidden = false;
        elements.formStatus.className = `form__status form__status--${type}`;

        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        elements.formStatus.innerHTML = `
            <div class="form__status-icon"><i class="fa-solid ${icon}"></i></div>
            <p class="form__status-message">${message}</p>
        `;

        if (type === 'success') {
            setTimeout(() => {
                elements.formStatus.hidden = true;
            }, 5000);
        }
    }

    function initContactForm() {
        if (!elements.contactForm) return;

        elements.contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = elements.contactSubmit;
            const originalText = submitBtn.innerHTML;

            // Disable button and show loading
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Envoi en cours...';

            // Hide previous status
            if (elements.formStatus) {
                elements.formStatus.hidden = true;
            }

            // Get form data
            const formData = new FormData(elements.contactForm);
            const data = {
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone') || null,
                subject: formData.get('subject'),
                message: formData.get('message')
            };

            try {
                const response = await fetch(`${API_BASE}/contact`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    showFormStatus('success', 'Votre message a ete envoye avec succes ! Nous vous repondrons rapidement.');
                    elements.contactForm.reset();
                } else {
                    const error = await response.json();
                    throw new Error(error.detail || 'Erreur lors de l\'envoi');
                }
            } catch (error) {
                console.error('Error submitting contact form:', error);
                showFormStatus('error', 'Une erreur est survenue. Veuillez reessayer plus tard.');
            } finally {
                // Re-enable button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // =====================================================
    // INITIALIZATION
    // =====================================================

    async function init() {
        // Initialize components
        initNavigation();
        initMenuControls();
        initHeaderScroll();
        initContactForm();

        // Fetch and render data from API
        await fetchProducts();

        // Render all sections (parallel)
        await Promise.all([
            renderBestsellers(),
            renderLocation(),
            renderSchedule()
        ]);

        // Render menu with fetched products
        renderMenu();

        // Initialize carousels after products are rendered
        initCarousels();

        // Start scroll animations
        observeAnimations();

        // Log ready
        console.log('KIOSQUE DU PARC - Site vitrine initialise (API mode)');
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
