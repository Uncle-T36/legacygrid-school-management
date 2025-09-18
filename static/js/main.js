/**
 * LegacyGrid School Management - Modern UI Interactions
 * Provides sidebar navigation, responsive behavior, and animations
 */

class LegacyGridUI {
  constructor() {
    this.sidebar = null;
    this.sidebarToggle = null;
    this.mainContent = null;
    this.init();
  }

  init() {
    this.setupElements();
    this.setupEventListeners();
    this.setupAnimations();
    this.handleResponsive();
  }

  setupElements() {
    this.sidebar = document.querySelector('.sidebar');
    this.sidebarToggle = document.querySelector('.sidebar-toggle');
    this.mainContent = document.querySelector('.main-content');
    this.navLinks = document.querySelectorAll('.nav-link');
  }

  setupEventListeners() {
    // Sidebar toggle for mobile
    if (this.sidebarToggle) {
      this.sidebarToggle.addEventListener('click', () => {
        this.toggleSidebar();
      });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 1024 && 
          this.sidebar && 
          this.sidebar.classList.contains('mobile-open') &&
          !this.sidebar.contains(e.target) && 
          !this.sidebarToggle.contains(e.target)) {
        this.closeSidebar();
      }
    });

    // Active navigation link highlighting
    this.setActiveNavLink();

    // Form enhancements
    this.enhanceForms();

    // Loading state for buttons
    this.setupButtonLoadingStates();

    // Keyboard navigation
    this.setupKeyboardNavigation();

    // Window resize handler
    window.addEventListener('resize', () => {
      this.handleResponsive();
    });
  }

  toggleSidebar() {
    if (window.innerWidth <= 1024) {
      // Mobile: toggle open/close
      if (this.sidebar) {
        this.sidebar.classList.toggle('mobile-open');
      }
    } else {
      // Desktop: toggle collapsed state
      if (this.sidebar) {
        this.sidebar.classList.toggle('collapsed');
        if (this.mainContent) {
          this.mainContent.classList.toggle('expanded');
        }
      }
    }
  }

  closeSidebar() {
    if (this.sidebar) {
      this.sidebar.classList.remove('mobile-open');
    }
  }

  setActiveNavLink() {
    const currentPath = window.location.pathname;
    
    this.navLinks.forEach(link => {
      link.classList.remove('active');
      
      const href = link.getAttribute('href');
      if (href && (currentPath === href || currentPath.startsWith(href + '/'))) {
        link.classList.add('active');
      }
    });
  }

  handleResponsive() {
    if (window.innerWidth <= 1024) {
      // Mobile/tablet: ensure sidebar is properly positioned
      if (this.sidebar) {
        this.sidebar.classList.remove('collapsed');
      }
      if (this.mainContent) {
        this.mainContent.classList.remove('expanded');
      }
    }
  }

  setupAnimations() {
    // Animate elements on page load
    const animatedElements = document.querySelectorAll('.card, .feature-card, .alert');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in');
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(el => {
      observer.observe(el);
    });
  }

  enhanceForms() {
    // Add floating labels and better validation
    const formGroups = document.querySelectorAll('.form-group');
    
    formGroups.forEach(group => {
      const input = group.querySelector('.form-control');
      const label = group.querySelector('.form-label');
      
      if (input && label) {
        // Add focus/blur effects
        input.addEventListener('focus', () => {
          group.classList.add('focused');
        });
        
        input.addEventListener('blur', () => {
          group.classList.remove('focused');
          if (input.value.trim() !== '') {
            group.classList.add('filled');
          } else {
            group.classList.remove('filled');
          }
        });

        // Initial state check
        if (input.value.trim() !== '') {
          group.classList.add('filled');
        }
      }
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
          this.showButtonLoading(submitBtn);
        }
      });
    });
  }

  setupButtonLoadingStates() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        // Only show loading for buttons that trigger navigation or forms
        if (btn.type === 'submit' || btn.href) {
          this.showButtonLoading(btn);
        }
      });
    });
  }

  showButtonLoading(button) {
    if (button.classList.contains('loading')) return;
    
    const originalContent = button.innerHTML;
    button.classList.add('loading');
    button.disabled = true;
    
    // Add spinner
    button.innerHTML = '<span class="spinner"></span>' + button.textContent;
    
    // Auto-remove loading state after timeout (fallback)
    setTimeout(() => {
      button.classList.remove('loading');
      button.disabled = false;
      button.innerHTML = originalContent;
    }, 10000);
  }

  hideButtonLoading(button) {
    button.classList.remove('loading');
    button.disabled = false;
    // Remove spinner if present
    const spinner = button.querySelector('.spinner');
    if (spinner) {
      spinner.remove();
    }
  }

  setupKeyboardNavigation() {
    // Escape key to close mobile sidebar
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeSidebar();
      }
    });

    // Arrow key navigation for nav links
    this.navLinks.forEach((link, index) => {
      link.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
          e.preventDefault();
          const direction = e.key === 'ArrowDown' ? 1 : -1;
          const nextIndex = (index + direction + this.navLinks.length) % this.navLinks.length;
          this.navLinks[nextIndex].focus();
        }
      });
    });
  }

  // Utility methods for external use
  showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.content-body') || document.body;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} animate-fade-in`;
    alert.innerHTML = `
      <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
      <button type="button" class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (alert.parentElement) {
        alert.remove();
      }
    }, 5000);
  }

  showModal(title, content, actions = []) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'modal card animate-fade-in';
    
    let actionsHtml = '';
    if (actions.length > 0) {
      actionsHtml = '<div class="modal-actions">' + 
        actions.map(action => `<button class="btn ${action.class || 'btn-secondary'}" onclick="${action.onclick || ''}">${action.text}</button>`).join('') +
        '</div>';
    }
    
    modal.innerHTML = `
      <div class="modal-header">
        <h3 class="modal-title">${title}</h3>
        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
      </div>
      <div class="modal-body">${content}</div>
      ${actionsHtml}
    `;
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // Close on overlay click
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.remove();
      }
    });
    
    // Close on escape
    const escapeHandler = (e) => {
      if (e.key === 'Escape') {
        overlay.remove();
        document.removeEventListener('keydown', escapeHandler);
      }
    };
    document.addEventListener('keydown', escapeHandler);
    
    return overlay;
  }

  // Theme switching (for future enhancement)
  toggleTheme() {
    // Future implementation for light/dark mode toggle
    console.log('Theme toggle - feature reserved for future enhancement');
  }
}

// Initialize the UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.LegacyGrid = new LegacyGridUI();
  
  // Add smooth scroll for anchor links
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
  
  // Add ripple effect to buttons
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;
      
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = x + 'px';
      ripple.style.top = y + 'px';
      ripple.classList.add('ripple');
      
      this.appendChild(ripple);
      
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LegacyGridUI;
}