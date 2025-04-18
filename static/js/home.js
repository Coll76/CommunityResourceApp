document.addEventListener('DOMContentLoaded', function() {
    // Counter animation function with improved easing
    function animateCounters() {
        const counters = document.querySelectorAll('.counter');
        const duration = 2000; // Animation duration in milliseconds
        
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const startTime = performance.now();
            let currentCount = 0;
            
            function updateCounter(currentTime) {
                const elapsedTime = currentTime - startTime;
                const progress = Math.min(elapsedTime / duration, 1);
                
                // Easing function for smoother animation
                const easedProgress = easeOutExpo(progress);
                currentCount = Math.floor(target * easedProgress);
                
                counter.innerText = formatNumber(currentCount);
                
                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.innerText = formatNumber(target);
                }
            }
            
            requestAnimationFrame(updateCounter);
        });
    }
    
    // Easing function for smoother counter animation
    function easeOutExpo(x) {
        return x === 1 ? 1 : 1 - Math.pow(2, -10 * x);
    }
    
    // Format numbers with commas for better readability
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
    
    // Enhanced intersection observer with staggered animations
    const observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -100px 0px'
    };
    
    // Observer for counter animation
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Small delay before starting counter animation
                setTimeout(() => {
                    animateCounters();
                }, 300);
                counterObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Apply counter observer to the stats section
    const statsSection = document.querySelector('.stats-card');
    if (statsSection) {
        counterObserver.observe(statsSection);
    }
    
    // Observer for card animations with improved timing
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add class with slight delay for staggered effect
                setTimeout(() => {
                    entry.target.classList.add('animated');
                }, 100);
                cardObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Apply card animations to all cards
    document.querySelectorAll('.card').forEach(card => {
        cardObserver.observe(card);
    });
    
    // Parallax effect for hero section
    const heroSection = document.querySelector('.jumbotron');
    if (heroSection) {
        window.addEventListener('scroll', () => {
            const scrollPosition = window.pageYOffset;
            if (scrollPosition < 600) {
                const translateY = scrollPosition * 0.3;
                heroSection.style.backgroundPositionY = `-${translateY}px`;
            }
        });
    }
    
    // Enhanced testimonial carousel functionality
    const testimonialCarousel = document.querySelector('.testimonials-carousel');
    if (testimonialCarousel) {
        // Initialize testimonial rotation if multiple testimonials exist
        const testimonials = testimonialCarousel.querySelectorAll('.testimonial-card');
        if (testimonials.length > 1) {
            let currentTestimonial = 0;
            setInterval(() => {
                testimonials[currentTestimonial].classList.add('testimonial-hiding');
                
                setTimeout(() => {
                    testimonials[currentTestimonial].classList.remove('active', 'testimonial-hiding');
                    currentTestimonial = (currentTestimonial + 1) % testimonials.length;
                    testimonials[currentTestimonial].classList.add('active');
                }, 500);
            }, 5000); // Rotate every 5 seconds
        }
    }
    
    // Add subtle hover effects to navigation elements
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Enhance search functionality if present
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[type="search"]');
        if (searchInput) {
            // Add focus effect
            searchInput.addEventListener('focus', function() {
                this.parentElement.classList.add('search-focused');
            });
            
            searchInput.addEventListener('blur', function() {
                this.parentElement.classList.remove('search-focused');
            });
        }
    }
    
    // Performance optimization for animations
    // Use requestAnimationFrame for smooth animations
    let ticking = false;
    
    function onScroll() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                handleScrollEffects();
                ticking = false;
            });
            
            ticking = true;
        }
    }
    
    function handleScrollEffects() {
        // Add scroll-based effects here
        const scrollPosition = window.scrollY;
        
        // Subtle parallax for sections
        document.querySelectorAll('.section-header').forEach(header => {
            const rect = header.getBoundingClientRect();
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                const parallaxValue = (rect.top / window.innerHeight) * 20;
                header.style.transform = `translateY(${parallaxValue}px)`;
            }
        });
    }
    
    // Add scroll listener for performance-optimized effects
    window.addEventListener('scroll', onScroll, { passive: true });
});