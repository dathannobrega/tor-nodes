// Enhanced JavaScript for the improved frontend
document.addEventListener("DOMContentLoaded", () => {
  // Smooth scrolling for navigation links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })

  // Mobile navigation toggle
  const navToggle = document.querySelector(".nav-toggle")
  const navLinks = document.querySelector(".nav-links")

  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      navLinks.classList.toggle("active")
      navToggle.classList.toggle("active")
    })
  }

  // Animated counter for hero stats
  function animateCounter(element, target, duration = 2000) {
    const start = 0
    const increment = target / (duration / 16)
    let current = start

    const timer = setInterval(() => {
      current += increment
      if (current >= target) {
        current = target
        clearInterval(timer)
      }
      element.textContent = Math.floor(current)
    }, 16)
  }

  // Initialize counters when they come into view
  const observerOptions = {
    threshold: 0.5,
    rootMargin: "0px 0px -100px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const target = Number.parseInt(entry.target.dataset.target) || 0
        animateCounter(entry.target, target)
        observer.unobserve(entry.target)
      }
    })
  }, observerOptions)

  document.querySelectorAll(".stat-number[data-target]").forEach((el) => {
    observer.observe(el)
  })

  // Script para funcionalidades interativas da página
  // Atualiza estatísticas em tempo real
  async function updateStats() {
    try {
      const response = await fetch("/status")
      const data = await response.json()

      // Update counters if data is available
      if (data.ip_count !== undefined) {
        const ipCountEl = document.querySelector("[data-target]")
        if (ipCountEl && !ipCountEl.dataset.animated) {
          ipCountEl.dataset.target = data.ip_count
        }
      }

      // Update status indicator
      const statusDot = document.querySelector(".status-dot")
      if (statusDot && data.status === "online") {
        statusDot.style.background = "var(--success)"
      }
    } catch (error) {
      console.log("Erro ao atualizar estatísticas:", error)
    }
  }

  // Função para animar números
  function animateNumber(element, targetNumber) {
    const currentNumber = Number.parseInt(element.textContent) || 0
    const increment = Math.ceil((targetNumber - currentNumber) / 20)

    if (currentNumber < targetNumber) {
      element.textContent = currentNumber + increment
      setTimeout(() => animateNumber(element, targetNumber), 50)
    } else {
      element.textContent = targetNumber
    }
  }

  // Adiciona efeito de hover nos cards
  const cards = document.querySelectorAll(".card")
  cards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-5px) scale(1.02)"
    })

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0) scale(1)"
    })
  })

  // Adiciona efeito de clique nos links sociais
  const socialLinks = document.querySelectorAll(".social-link")
  socialLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      // Efeito visual de clique
      this.style.transform = "scale(0.95)"
      setTimeout(() => {
        this.style.transform = "scale(1.05)"
      }, 100)
    })
  })

  // Code tabs functionality
  const codeTabs = document.querySelectorAll(".code-tab")
  const codeBlocks = document.querySelectorAll(".code-block")

  codeTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const lang = tab.dataset.lang

      // Remove active class from all tabs and blocks
      codeTabs.forEach((t) => t.classList.remove("active"))
      codeBlocks.forEach((b) => b.classList.remove("active"))

      // Add active class to clicked tab and corresponding block
      tab.classList.add("active")
      document.querySelector(`.code-block[data-lang="${lang}"]`).classList.add("active")
    })
  })

  // Copy code to clipboard
  document.querySelectorAll(".code-block pre").forEach((block) => {
    block.style.cursor = "pointer"
    block.title = "Clique para copiar"

    block.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(block.textContent)

        // Visual feedback
        const originalBg = block.style.background
        block.style.background = "rgba(0, 255, 136, 0.1)"
        block.style.transition = "background 0.3s ease"

        setTimeout(() => {
          block.style.background = originalBg
        }, 1000)

        // Show notification
        showNotification("Código copiado!", "success")
      } catch (err) {
        showNotification("Erro ao copiar código", "error")
      }
    })
  })

  // Navbar scroll effect
  let lastScrollY = window.scrollY
  const navbar = document.querySelector(".navbar")

  window.addEventListener("scroll", () => {
    const currentScrollY = window.scrollY

    if (currentScrollY > 100) {
      navbar.style.background = "rgba(10, 10, 10, 0.95)"
    } else {
      navbar.style.background = "rgba(10, 10, 10, 0.9)"
    }

    lastScrollY = currentScrollY
  })

  // Parallax effect for background
  window.addEventListener("scroll", () => {
    const scrolled = window.pageYOffset
    const parallax = document.querySelector(".bg-effects")
    if (parallax) {
      parallax.style.transform = `translateY(${scrolled * 0.5}px)`
    }
  })

  // Copia código para clipboard quando clicado
  /*const codeBlocksOld = document.querySelectorAll(".code-example, .code-block")
  codeBlocksOld.forEach((block) => {
    block.style.cursor = "pointer"
    block.title = "Clique para copiar"

    block.addEventListener("click", function () {
      navigator.clipboard
        .writeText(this.textContent.trim())
        .then(() => {
          // Feedback visual
          const originalBorder = this.style.borderLeft
          this.style.borderLeft = "3px solid #00ffff"
          this.style.background = "rgba(0, 255, 255, 0.1)"

          setTimeout(() => {
            this.style.borderLeft = originalBorder
            this.style.background = "rgba(0, 0, 0, 0.5)"
          }, 1000)
        })
        .catch((err) => {
          console.log("Erro ao copiar:", err)
        })
    })
  })*/

  // Initialize
  updateStats()

  // Update stats every 30 seconds
  setInterval(updateStats, 30000)

  // Adiciona efeito de digitação no título
  const title = document.querySelector(".main-title")
  if (title) {
    const originalText = title.textContent
    title.textContent = ""

    let i = 0
    const typeWriter = () => {
      if (i < originalText.length) {
        title.textContent += originalText.charAt(i)
        i++
        setTimeout(typeWriter, 100)
      }
    }

    // Inicia o efeito após um pequeno delay
    setTimeout(typeWriter, 500)
  }

  // Add fade-in animation to sections
  const sections = document.querySelectorAll(".section")
  const sectionObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("fade-in-up")
        }
      })
    },
    { threshold: 0.1 },
  )

  sections.forEach((section) => {
    sectionObserver.observe(section)
  })

  // Easter egg: Konami code
  let konamiCode = []
  const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65] // ↑↑↓↓←→←→BA

  document.addEventListener("keydown", (e) => {
    konamiCode.push(e.keyCode)
    if (konamiCode.length > konamiSequence.length) {
      konamiCode.shift()
    }

    if (konamiCode.join(",") === konamiSequence.join(",")) {
      showNotification("🧅 Código Konami ativado! Você é um verdadeiro hacker!", "success")
      document.body.style.filter = "hue-rotate(180deg)"
      setTimeout(() => {
        document.body.style.filter = "none"
      }, 3000)
      konamiCode = []
    }
  })
})

// Função para scroll suave
function smoothScroll(target) {
  document.querySelector(target).scrollIntoView({
    behavior: "smooth",
  })
}

// Adiciona funcionalidade de tema escuro/claro (opcional)
function toggleTheme() {
  document.body.classList.toggle("light-theme")
  localStorage.setItem("theme", document.body.classList.contains("light-theme") ? "light" : "dark")
}

// Carrega tema salvo
if (localStorage.getItem("theme") === "light") {
  document.body.classList.add("light-theme")
}

// Adiciona função para testar endpoints da API
/*function testApiEndpoint(endpoint) {
  fetch(endpoint)
    .then((response) => response.json())
    .then((data) => {
      console.log(`Dados de ${endpoint}:`, data)
      // Mostra notificação visual
      showNotification(`Dados carregados de ${endpoint}`)
    })
    .catch((error) => {
      console.error(`Erro ao buscar ${endpoint}:`, error)
      showNotification(`Erro ao carregar ${endpoint}`, "error")
    })
}*/

// Função para mostrar notificações
function showNotification(message, type = "info") {
  const notification = document.createElement("div")
  notification.className = `notification notification-${type}`
  notification.textContent = message

  notification.style.cssText = `
    position: fixed;
    top: 100px;
    right: 24px;
    padding: 16px 24px;
    background: ${type === "success" ? "var(--success)" : "var(--error)"};
    color: var(--dark);
    border-radius: var(--border-radius);
    font-weight: 600;
    z-index: 10000;
    transform: translateX(400px);
    transition: transform 0.3s ease;
    box-shadow: var(--shadow);
  `

  document.body.appendChild(notification)

  // Animate in
  setTimeout(() => {
    notification.style.transform = "translateX(0)"
  }, 100)

  // Animate out and remove
  setTimeout(() => {
    notification.style.transform = "translateX(400px)"
    setTimeout(() => {
      document.body.removeChild(notification)
    }, 300)
  }, 3000)
}

// Global functions
window.torNodes = {
  // Test API endpoint
  testEndpoint: async (endpoint) => {
    try {
      const response = await fetch(endpoint)
      const data = await response.json()
      console.log(`Dados de ${endpoint}:`, data)
      return data
    } catch (error) {
      console.error(`Erro ao testar ${endpoint}:`, error)
      return null
    }
  },

  // Get all nodes
  getAllNodes: async function () {
    return await this.testEndpoint("/api/nodes")
  },

  // Get running nodes
  getRunningNodes: async function () {
    return await this.testEndpoint("/api/nodes/running")
  },

  // Get nodes by country
  getNodesByCountry: async function (country) {
    return await this.testEndpoint(`/api/nodes/country/${country}`)
  },

  // Get statistics
  getStats: async function () {
    return await this.testEndpoint("/api/stats")
  },
}
