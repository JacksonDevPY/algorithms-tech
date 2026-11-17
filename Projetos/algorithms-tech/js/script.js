window.addEventListener('load', () => {
    document.body.classList.remove('loading-hidden');
    
    if (typeof gsap !== 'undefined') {
        gsap.from(".hero-content > *", { 
            y: 30, 
            opacity: 0, 
            duration: 1, 
            stagger: 0.2,
            ease: "power2.out"
        });
    }
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetID = this.getAttribute('href');
        
        if (targetID === "#") {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            const targetElement = document.querySelector(targetID);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
});

const contatoForm = document.querySelector('form');

if (contatoForm) {
    contatoForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const nome = this.querySelector('input[placeholder="Seu nome"]').value;
        const email = this.querySelector('input[placeholder="Seu e-mail"]').value;
        const mensagem = this.querySelector('textarea[placeholder="Sua mensagem"]').value;

        const meuNumero = "5594991569871";
        
        const textoFormatado = `*NOVO ORÇAMENTO - ALGORITHM'S TECH*%0A` +
                               `------------------------------------%0A` +
                               `*👤 Nome:* ${nome}%0A` +
                               `*📧 E-mail:* ${email}%0A` +
                               `*📋 Assunto:* Solicitação de Orçamento%0A` +
                               `------------------------------------%0A` +
                               `*💬 Mensagem:*%0A${mensagem}`;

        const urlWhatsapp = `https://wa.me/${meuNumero}?text=${textoFormatado}`;

        window.open(urlWhatsapp, '_blank');
        this.reset();
    });
}
