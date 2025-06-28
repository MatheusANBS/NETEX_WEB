console.log('Arquivo de teste carregado!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado - teste');
    
    // Teste básico de seleção de elementos
    const ssInput = document.getElementById('ss');
    const skInput = document.getElementById('sk');
    const gerarCorteBtn = document.getElementById('gerar-corte');
    
    console.log('Elementos encontrados:', {
        ss: !!ssInput,
        sk: !!skInput,
        gerarCorte: !!gerarCorteBtn
    });
    
    // Teste de evento simples
    if (ssInput) {
        ssInput.addEventListener('input', function() {
            console.log('Input SS mudou:', this.value);
        });
    }
    
    if (gerarCorteBtn) {
        gerarCorteBtn.addEventListener('click', function() {
            console.log('Botão de gerar corte clicado!');
        });
    }
});
