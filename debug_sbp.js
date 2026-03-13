document.addEventListener("DOMContentLoaded", () => {

    const body = document.querySelector("body");
    const isDark = document.body.classList.contains('theme-dark');
    var logoContainer = document.getElementById("formIconSbp");
    var headerContent = document.querySelector(".form-header_content");


    document.body.style.setProperty('--circle-color', 'rgba(38, 173, 80, .2)');
    body.classList.add('route-sbp');
    const backLink = document.querySelector(".back-link_header");
    backLink.style.display = "flex";
    var currentBackLink = document.getElementById("backLink");
    var globalLoader = document.getElementById("globalLoader");

    function handleResize() {
        if(document.getElementById("qr-code")){
            var formFooterDesktop = document.querySelector(".form-footer-desktop");
            if(formFooterDesktop){
                if((window.innerWidth > window.mobileBreakpoint) && (window.innerWidth < window.tabletBreakpoint)){
                    formFooterDesktop.style.display = "block";
                }else if(window.innerWidth < window.mobileBreakpoint){
                    const formWrapper = document.getElementById("formWrapper");
                    formWrapper.style.marginBottom = "32px";
                    formFooterDesktop.style.display = "none";
                }
            }
        }

        if((window.innerWidth < window.mobileBreakpoint) && (window.innerWidth > 431) && currentBackLink){
            currentBackLink.style.marginTop = "16px";
        }
        mobileCorrector();
        if (window.innerWidth < window.mobileBreakpoint) {
            backLink.style.display = "none";
            if(logoContainer){
                logoContainer.style.display = "block";
                headerContent.style.alignItems = "start";
                logoContainer.style.marginTop = "5px";
            }

        } else {
            backLink.style.display = "flex";
            if(logoContainer){
                logoContainer.style.display = "none";
            }
        }
    }


    function setIcons(){
        const isDark = document.body.classList.contains('theme-dark');
        const arrows = document.querySelectorAll('.arrow-right-icon');
        arrows.forEach((arrow) => {
            arrow.src = isDark
                ? '/nova/img/icons/arrow-right-dark.svg'
                : '/nova/img/icons/arrow-right.svg';
        })
        const pciIcon = document.querySelectorAll('.pci-icon');
        const logo = document.getElementById("logo");
        if(pciIcon.length > 0){
            pciIcon.forEach((icon) => {
                icon.src = isDark
                    ? '/nova/img/icons/webp/lock-dark.webp'
                    : '/nova/img/icons/webp/lock.webp';
            });
        }
        if(logo){
            logo.src = isDark
                ? '/nova/img/icons/logo-dark.svg'
                : '/nova/img/icons/logo.svg';
        }
    }
    setIcons();
    const observer = new MutationObserver(() => {
        setIcons();
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });

    function mobileCorrector(){
        const isMobile = /iPhone|iPad|iPod|Android|Mobile/i.test(navigator.userAgent);
        const formFooterMobile = document.getElementById("formFooterMobile");
        const main = document.querySelector("main");
        if(isMobile && window.innerWidth < window.mobileBreakpoint){
            var bankListWrapper = document.querySelector(".bank-list-wrapper");
            if(bankListWrapper){
                bankListWrapper.style.margin = "24px 0 8px 0";
                formFooterMobile.style.display = "block";
                main.style.minHeight = "calc(100dvh)";
            }

        }
    }
    mobileCorrector();
    handleResize();
    window.addEventListener("resize", handleResize);
});
