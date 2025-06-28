// Corteus App - Versão Simplificada para Debug
console.log('Corteus App JavaScript carregado! (versão debug)');

// Função para aguardar que todos os recursos estejam carregados
function whenReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}

whenReady(function() {
    console.log('DOM carregado - iniciando aplicação');
    
    // Verificar se elementos essenciais existem
    const elementos = {
        'ss': document.getElementById('ss'),
        'sk': document.getElementById('sk'),
        'cod_material': document.getElementById('cod_material'),
        'cortes_desejados': document.getElementById('cortes_desejados'),
        'barras_disponiveis': document.getElementById('barras_disponiveis'),
        'gerar-corte': document.getElementById('gerar-corte'),
        'gerar-minuta': document.getElementById('gerar-minuta'),
        'help-button': document.getElementById('help-button'),
        'tutorial-modal': document.getElementById('tutorial-modal'),
        'close-tutorial': document.getElementById('close-tutorial'),
        'ss-error': document.getElementById('ss-error'),
        'sk-error': document.getElementById('sk-error'),
        'cod-error': document.getElementById('cod-error'),
        'cortes-error': document.getElementById('cortes-error'),
        'barras-error': document.getElementById('barras-error')
    };
    
    console.log('Elementos encontrados:', elementos);
    
    // Contabilizar elementos faltantes
    const faltantes = Object.keys(elementos).filter(key => !elementos[key]);
    if (faltantes.length > 0) {
        console.error('Elementos faltantes:', faltantes);
    } else {
        console.log('Todos os elementos encontrados!');
    }
    
    // Configurar validação básica do SS
    if (elementos.ss && elementos['ss-error']) {
        elementos.ss.addEventListener('input', function() {
            const valor = this.value.trim();
            const errorEl = elementos['ss-error'];
            
            console.log('Validando SS:', valor);
            
            if (valor && !/^\d{4}\/\d{4}$/.test(valor)) {
                errorEl.textContent = 'SS deve ter o formato 0123/2024';
                errorEl.classList.remove('hidden');
                this.classList.add('border-red-500');
                console.log('SS inválido');
            } else {
                errorEl.classList.add('hidden');
                this.classList.remove('border-red-500');
                console.log('SS válido');
            }
        });
        console.log('Validação SS configurada');
    }
    
    // Configurar validação básica do SK
    if (elementos.sk && elementos['sk-error']) {
        elementos.sk.addEventListener('input', function() {
            // Auto-uppercase
            this.value = this.value.toUpperCase();
            
            const valor = this.value.trim();
            const errorEl = elementos['sk-error'];
            
            console.log('Validando SK:', valor);
            
            if (valor && !/^[A-Z]{3}-\d{3}$/.test(valor)) {
                errorEl.textContent = 'SK deve ter o formato EST-001';
                errorEl.classList.remove('hidden');
                this.classList.add('border-red-500');
                console.log('SK inválido');
            } else {
                errorEl.classList.add('hidden');
                this.classList.remove('border-red-500');
                console.log('SK válido');
            }
        });
        console.log('Validação SK configurada');
    }
    
    // Configurar botão de gerar corte
    if (elementos['gerar-corte']) {
        elementos['gerar-corte'].addEventListener('click', function() {
            console.log('Botão gerar corte clicado!');
            
            // Validação básica
            const ss = elementos.ss.value.trim();
            const sk = elementos.sk.value.trim();
            const cod = elementos['cod_material'].value.trim();
            
            if (!ss || !sk || !cod) {
                alert('Preencha os campos obrigatórios: SS, SK e Código do Material');
                return;
            }
            
            console.log('Enviando requisição...');
            
            // Mostrar loading
            const loadingOverlay = document.getElementById('loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.classList.remove('hidden');
            }
            
            // Simular requisição (substitua pela requisição real)
            setTimeout(() => {
                if (loadingOverlay) {
                    loadingOverlay.classList.add('hidden');
                }
                
                // Mostrar resultado fictício
                const resultadoEl = document.getElementById('resultado-corte');
                if (resultadoEl) {
                    resultadoEl.innerHTML = `
                        <div class="mt-4 p-4 bg-green-900 border border-green-500 rounded-lg">
                            <div class="flex items-center mb-2">
                                <i class="fas fa-check-circle text-green-400 mr-2"></i>
                                <span class="text-green-100 font-medium">Relatório gerado com sucesso!</span>
                            </div>
                            <button class="mt-3 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded transition-all">
                                <i class="fas fa-download mr-2"></i>Baixar PDF
                            </button>
                        </div>
                    `;
                    resultadoEl.classList.remove('hidden');
                    console.log('Resultado mostrado');
                }
            }, 2000);
        });
        console.log('Event listener gerar corte configurado');
    }
    
    // Configurar tutorial modal
    if (elementos['help-button'] && elementos['tutorial-modal'] && elementos['close-tutorial']) {
        elementos['help-button'].addEventListener('click', function() {
            console.log('Abrindo tutorial');
            elementos['tutorial-modal'].classList.remove('hidden');
        });
        
        elementos['close-tutorial'].addEventListener('click', function() {
            console.log('Fechando tutorial');
            elementos['tutorial-modal'].classList.add('hidden');
        });
        
        elementos['tutorial-modal'].addEventListener('click', function(e) {
            if (e.target === this) {
                console.log('Fechando tutorial (clique fora)');
                this.classList.add('hidden');
            }
        });
        
        console.log('Tutorial modal configurado');
    }
    
    console.log('Aplicação inicializada com sucesso!');
});
