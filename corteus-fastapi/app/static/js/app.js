// Corteus App - Versão Funcional
console.log('=== CORTEUS APP INICIANDO ===');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, iniciando aplicação...');
    
    // Verificar se elementos existem
    const elementos = {
        'gerar-corte': document.getElementById('gerar-corte'),
        'gerar-minuta': document.getElementById('gerar-minuta'),
        'ss': document.getElementById('ss'),
        'sk': document.getElementById('sk'),
        'modo-automatico': document.querySelector('input[value="Automático"]'),
        'modo-manual': document.querySelector('input[value="Manual"]')
    };
    
    console.log('Elementos encontrados:', elementos);
    
    // Setup básico dos eventos
    setupEventListeners();
    setupModeToggle();
    setupValidations();
    setupModal();
    
    console.log('=== CORTEUS APP INICIALIZADO ===');
});

function setupEventListeners() {
    console.log('Configurando event listeners...');
    
    // Botões principais
    const btnCorte = document.getElementById('gerar-corte');
    const btnMinuta = document.getElementById('gerar-minuta');
    
    if (btnCorte) {
        btnCorte.addEventListener('click', gerarCorte);
        console.log('Event listener adicionado ao botão de corte');
    }
    
    if (btnMinuta) {
        btnMinuta.addEventListener('click', gerarMinuta);
        console.log('Event listener adicionado ao botão de minuta');
    }
    
    // Help button
    const helpBtn = document.getElementById('help-button');
    if (helpBtn) {
        helpBtn.addEventListener('click', showTutorial);
        console.log('Event listener adicionado ao botão de ajuda');
    }
    
    // Close tutorial
    const closeBtn = document.getElementById('close-tutorial');
    if (closeBtn) {
        closeBtn.addEventListener('click', hideTutorial);
    }
    
    // Modal click outside to close
    const modal = document.getElementById('tutorial-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target.id === 'tutorial-modal') {
                hideTutorial();
            }
        });
    }
    
    // Auto-uppercase para SK
    const skField = document.getElementById('sk');
    if (skField) {
        skField.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
            validarSK();
        });
        console.log('Event listener adicionado ao campo SK');
    }
    
    // Validações em tempo real
    const ssField = document.getElementById('ss');
    if (ssField) {
        ssField.addEventListener('input', validarSS);
        ssField.addEventListener('blur', validarSS);
    }
    
    const codField = document.getElementById('cod_material');
    if (codField) {
        codField.addEventListener('input', validarCodMaterial);
        codField.addEventListener('blur', validarCodMaterial);
    }
    
    const cortesField = document.getElementById('cortes_desejados');
    if (cortesField) {
        cortesField.addEventListener('input', validarCortes);
        cortesField.addEventListener('blur', validarCortes);
    }
    
    const barrasField = document.getElementById('barras_disponiveis');
    if (barrasField) {
        barrasField.addEventListener('input', validarBarras);
        barrasField.addEventListener('blur', validarBarras);
    }
    
    console.log('Event listeners configurados');
}

function setupModeToggle() {
    console.log('Configurando toggle de modo...');
    
    const radioButtons = document.querySelectorAll('input[name="modo"]');
    const modoAutomatico = document.getElementById('modo-automatico');
    const modoManual = document.getElementById('modo-manual');
    const emendaContainer = document.getElementById('emenda-container');
    
    console.log('Elementos de modo encontrados:', {
        radioButtons: radioButtons.length,
        modoAutomatico: !!modoAutomatico,
        modoManual: !!modoManual,
        emendaContainer: !!emendaContainer
    });
    
    // Função para atualizar a visibilidade
    function updateModeVisibility(modo) {
        console.log('=== Atualizando visibilidade para modo:', modo, '===');
        
        if (modo === 'Automático') {
            // Mostrar modo automático
            if (modoAutomatico) {
                modoAutomatico.classList.remove('hidden');
                console.log('✓ Modo automático mostrado');
            }
            // Ocultar modo manual
            if (modoManual) {
                modoManual.classList.add('hidden');
                console.log('✓ Modo manual ocultado');
            }
            // Ocultar emenda
            if (emendaContainer) {
                emendaContainer.classList.add('hidden');
                console.log('✓ Container de emenda ocultado');
            }
        } else if (modo === 'Manual') {
            // Ocultar modo automático
            if (modoAutomatico) {
                modoAutomatico.classList.add('hidden');
                console.log('✓ Modo automático ocultado');
            }
            // Mostrar modo manual
            if (modoManual) {
                modoManual.classList.remove('hidden');
                console.log('✓ Modo manual mostrado');
            }
            // Mostrar emenda
            if (emendaContainer) {
                emendaContainer.classList.remove('hidden');
                console.log('✓ Container de emenda mostrado');
            }
        }
        
        console.log('=== Fim da atualização ===');
    }
    
    // Função para verificar o modo atual
    function getCurrentMode() {
        const checkedRadio = document.querySelector('input[name="modo"]:checked');
        const modo = checkedRadio ? checkedRadio.value : null;
        console.log('Modo atual detectado:', modo);
        return modo;
    }
    
    // Configurar estado inicial
    const modoInicial = getCurrentMode();
    if (modoInicial) {
        console.log('Configurando estado inicial para:', modoInicial);
        updateModeVisibility(modoInicial);
    } else {
        console.log('Nenhum modo detectado, usando Automático como padrão');
        updateModeVisibility('Automático');
    }
    
    // Adicionar listeners para mudanças
    radioButtons.forEach((radio, index) => {
        console.log(`Adicionando listener ao radio ${index}: ${radio.value}`);
        radio.addEventListener('change', function(e) {
            console.log('🔄 Modo alterado para:', e.target.value);
            updateModeVisibility(e.target.value);
        });
    });
    
    console.log('Setup de modo concluído com sucesso!');
}

function setupValidations() {
    console.log('Configurando validações...');
    
    // Adicionar eventos de focus para limpar erros
    const campos = ['ss', 'sk', 'cod_material', 'cortes_desejados', 'barras_disponiveis'];
    
    campos.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('focus', () => clearFieldError(id));
        }
    });
}

function setupModal() {
    // ESC key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideTutorial();
        }
    });
}

// Validações
function validarSS() {
    const ss = document.getElementById('ss').value.trim();
    const errorElement = document.getElementById('ss-error');
    
    if (!ss) {
        hideError(errorElement);
        return true;
    }
    
    const regex = /^\d{4}\/\d{4}$/;
    if (!regex.test(ss)) {
        showError(errorElement, 'SS deve ter o formato 0123/2024');
        return false;
    }
    
    const ano = parseInt(ss.split('/')[1]);
    const anoAtual = new Date().getFullYear();
    const anoMin = anoAtual - 1;
    const anoMax = anoAtual + 4;
    
    if (ano < anoMin || ano > anoMax) {
        showError(errorElement, `O ano deve estar entre ${anoMin} e ${anoMax}`);
        return false;
    }
    
    hideError(errorElement);
    return true;
}

function validarSK() {
    const sk = document.getElementById('sk').value.trim();
    const errorElement = document.getElementById('sk-error');
    
    if (!sk) {
        hideError(errorElement);
        return true;
    }
    
    // Aceita formatos EST-123 ou TU-123
    const regex = /^(EST|TU)-\d{3}$/;
    if (!regex.test(sk)) {
        showError(errorElement, 'SK deve ter o formato EST-001 ou TU-001');
        return false;
    }
    
    hideError(errorElement);
    return true;
}

function validarCodMaterial() {
    const cod = document.getElementById('cod_material').value.trim();
    const errorElement = document.getElementById('cod-error');
    
    if (!cod) {
        hideError(errorElement);
        return true;
    }
    
    if (!/^\d{10}$/.test(cod)) {
        showError(errorElement, 'Código deve ter exatamente 10 dígitos');
        return false;
    }
    
    hideError(errorElement);
    return true;
}

function validarCortes() {
    const cortes = document.getElementById('cortes_desejados').value.trim();
    const errorElement = document.getElementById('cortes-error');
    
    if (!cortes) {
        hideError(errorElement);
        return true;
    }
    
    try {
        const cortesArray = parseNumeros(cortes);
        if (cortesArray.length === 0) {
            showError(errorElement, 'Informe pelo menos um corte');
            return false;
        }
        if (cortesArray.some(c => c <= 0)) {
            showError(errorElement, 'Todos os cortes devem ser maiores que zero');
            return false;
        }
        if (cortesArray.some(c => c > 6000)) {
            showError(errorElement, 'Cortes muito grandes (máx: 6000mm)');
            return false;
        }
        hideError(errorElement);
        return true;
    } catch (e) {
        showError(errorElement, 'Formato inválido. Use números separados por vírgula, espaço ou quebra de linha');
        return false;
    }
}

function validarBarras() {
    const barras = document.getElementById('barras_disponiveis').value.trim();
    const errorElement = document.getElementById('barras-error');
    
    if (!barras) {
        hideError(errorElement);
        return true;
    }
    
    try {
        const barrasArray = parseNumeros(barras);
        if (barrasArray.length === 0) {
            showError(errorElement, 'Informe pelo menos uma barra');
            return false;
        }
        if (barrasArray.some(b => b <= 0)) {
            showError(errorElement, 'Todas as barras devem ser maiores que zero');
            return false;
        }
        hideError(errorElement);
        return true;
    } catch (e) {
        showError(errorElement, 'Formato inválido. Use números separados por vírgula, espaço ou quebra de linha');
        return false;
    }
}

function parseNumeros(str) {
    // Suporta separação por vírgula, espaço, quebra de linha ou combinações
    const numeros = str.split(/[,\s\n\r]+/)
              .map(s => s.trim())
              .filter(s => s !== '')
              .map(s => {
                  const num = parseInt(s);
                  if (isNaN(num)) throw new Error('Valor inválido');
                  return num;
              });
    
    console.log('parseNumeros:', str, '->', numeros);
    return numeros;
}

function showError(element, message) {
    console.log('Mostrando erro:', message);
    if (element) {
        element.textContent = message;
        element.classList.remove('hidden');
        
        const input = element.parentElement.querySelector('input, textarea, select');
        if (input) {
            input.classList.add('border-red-500', 'border-2');
            input.classList.remove('border-gray-600');
        }
    }
}

function hideError(element) {
    if (element) {
        element.classList.add('hidden');
        
        const input = element.parentElement.querySelector('input, textarea, select');
        if (input) {
            input.classList.remove('border-red-500', 'border-2');
            input.classList.add('border-gray-600');
        }
    }
}

function clearFieldError(fieldId) {
    const errorElement = document.getElementById(fieldId + '-error');
    if (errorElement) {
        hideError(errorElement);
    }
}

// Coleta dados do formulário
function coletarDados() {
    const modoChecked = document.querySelector('input[name="modo"]:checked');
    const modo = modoChecked ? modoChecked.value : 'Automático';
    
    const dados = {
        projeto: document.getElementById('projeto').value,
        ss: document.getElementById('ss').value.trim(),
        sk: document.getElementById('sk').value.trim(),
        cod_material: document.getElementById('cod_material').value.trim(),
        modo: modo,
        sugestao_emenda: document.getElementById('sugestao_emenda').checked,
        cortes_desejados: parseNumeros(document.getElementById('cortes_desejados').value)
    };
    
    if (modo === 'Automático') {
        dados.comprimento_barra = parseInt(document.getElementById('comprimento_barra').value);
    } else {
        const barrasInput = document.getElementById('barras_disponiveis').value.trim();
        dados.barras_disponiveis = barrasInput ? parseNumeros(barrasInput) : [];
    }
    
    return dados;
}

// Validar formulário completo
function validarFormulario() {
    console.log('Validando formulário...');
    
    const ss = validarSS();
    const sk = validarSK();
    const cod = validarCodMaterial();
    const cortes = validarCortes();
    
    const dados = coletarDados();
    console.log('Dados coletados:', dados);
    
    // Verificar campos obrigatórios
    if (!dados.ss || !dados.sk || !dados.cod_material || !dados.cortes_desejados.length) {
        console.log('Campos obrigatórios em falta');
        showAlert('error', 'Preencha todos os campos obrigatórios');
        return false;
    }
    
    if (dados.modo === 'Automático' && !dados.comprimento_barra) {
        showAlert('error', 'Informe o comprimento da barra no modo automático');
        return false;
    }
    
    if (dados.modo === 'Manual' && !dados.barras_disponiveis.length) {
        validarBarras();
        showAlert('error', 'Informe as barras disponíveis no modo manual');
        return false;
    }
    
    const isValid = ss && sk && cod && cortes;
    console.log('Formulário válido:', isValid);
    return isValid;
}

// Gerar relatório de corte
async function gerarCorte() {
    console.log('=== GERANDO CORTE ===');
    
    if (!validarFormulario()) {
        console.log('Validação falhou');
        return;
    }
    
    const dados = coletarDados();
    console.log('Dados para envio:', dados);
    
    const resultadoEl = document.getElementById('resultado-corte');
    
    showLoading('Gerando relatório de corte...');
    
    try {
        console.log('Enviando requisição para /api/cortes/gerar');
        
        const response = await fetch('/api/cortes/gerar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dados)
        });
        
        console.log('Response status:', response.status);
        const resultado = await response.json();
        console.log('Resultado recebido:', resultado);
        
        hideLoading();
        
        if (response.ok && resultado.sucesso) {
            showResult(resultadoEl, 'success', resultado.resultado, resultado.nome_arquivo, 'corte');
            
            // Google Analytics
            if (typeof gtag !== 'undefined') {
                gtag('event', 'relatorio_gerado', {
                    'event_category': 'corte',
                    'event_label': dados.modo
                });
            }
        } else {
            const errorMsg = resultado.detail || resultado.erro || 'Erro ao gerar relatório';
            console.log('Erro na resposta:', errorMsg);
            showResult(resultadoEl, 'error', errorMsg);
        }
        
    } catch (error) {
        console.error('Erro na requisição:', error);
        hideLoading();
        showResult(resultadoEl, 'error', 'Erro de conexão. Tente novamente.');
    }
}

// Gerar relatório de minuta
async function gerarMinuta() {
    console.log('=== GERANDO MINUTA ===');
    
    if (!validarFormulario()) return;
    
    const dados = coletarDados();
    
    // Validação específica da minuta
    if (dados.cortes_desejados.some(c => c > 6000)) {
        showAlert('error', 'Não é possível gerar minuta com cortes maiores que 6000mm');
        return;
    }
    
    const resultadoEl = document.getElementById('resultado-minuta');
    
    showLoading('Gerando relatório de minuta...');
    
    try {
        const dadosMinuta = {
            projeto: dados.projeto,
            ss: dados.ss,
            sk: dados.sk,
            cod_material: dados.cod_material,
            cortes_desejados: dados.cortes_desejados
        };
        
        const response = await fetch('/api/minuta/gerar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dadosMinuta)
        });
        
        const resultado = await response.json();
        console.log('Resultado minuta:', resultado);
        
        hideLoading();
        
        if (response.ok && resultado.sucesso) {
            showResult(resultadoEl, 'success', resultado.resultado, resultado.nome_arquivo, 'minuta');
            
            // Google Analytics
            if (typeof gtag !== 'undefined') {
                gtag('event', 'relatorio_gerado', {
                    'event_category': 'minuta',
                    'event_label': 'manual'
                });
            }
        } else {
            const errorMsg = resultado.detail || resultado.erro || 'Erro ao gerar minuta';
            showResult(resultadoEl, 'error', errorMsg);
        }
        
    } catch (error) {
        console.error('Erro:', error);
        hideLoading();
        showResult(resultadoEl, 'error', 'Erro de conexão. Tente novamente.');
    }
}

// Mostrar resultado
function showResult(element, type, message, fileName = null, fileType = null) {
    console.log('Mostrando resultado:', {type, message, fileName, fileType});
    
    if (!element) {
        console.error('Elemento de resultado não encontrado');
        return;
    }
    
    element.classList.remove('hidden');
    element.innerHTML = '';
    
    if (type === 'success') {
        element.className = 'mt-4 p-4 bg-green-900 border border-green-500 rounded-lg';
        
        const successDiv = document.createElement('div');
        successDiv.className = 'flex items-center mb-2';
        successDiv.innerHTML = `
            <i class="fas fa-check-circle text-green-400 mr-2"></i>
            <span class="text-green-100 font-medium">${message}</span>
        `;
        element.appendChild(successDiv);
        
        if (fileName) {
            console.log('Adicionando botão de download para:', fileName);
            
            const downloadBtn = document.createElement('button');
            downloadBtn.className = 'mt-3 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded transition-all';
            downloadBtn.innerHTML = '<i class="fas fa-download mr-2"></i>Baixar PDF';
            downloadBtn.onclick = () => {
                console.log('Download clicado:', fileName, fileType);
                downloadPDF(fileName, fileType);
            };
            element.appendChild(downloadBtn);
        }
    } else {
        element.className = 'mt-4 p-4 bg-red-900 border border-red-500 rounded-lg';
        element.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle text-red-400 mr-2"></i>
                <span class="text-red-100">${message}</span>
            </div>
        `;
    }
}

// Loading overlay
function showLoading(message) {
    const overlay = document.getElementById('loading-overlay');
    const text = document.getElementById('loading-text');
    if (overlay && text) {
        text.textContent = message;
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

// Alert genérico
function showAlert(type, message) {
    console.log('Exibindo alerta:', type, message);
    
    // Criar toast notification
    const alert = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-600' : 'bg-blue-600';
    alert.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-4 rounded-lg shadow-lg z-50 transform transition-all duration-300`;
    alert.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(alert);
    
    // Animar entrada
    setTimeout(() => alert.classList.add('translate-x-0'), 100);
    
    // Remover após 5 segundos
    setTimeout(() => {
        alert.classList.add('translate-x-full');
        setTimeout(() => {
            if (document.body.contains(alert)) {
                document.body.removeChild(alert);
            }
        }, 300);
    }, 5000);
}

// Tutorial modal
function showTutorial() {
    const modal = document.getElementById('tutorial-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function hideTutorial() {
    const modal = document.getElementById('tutorial-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Download PDF
function downloadPDF(nomeArquivo, tipo) {
    console.log('Iniciando download:', nomeArquivo, tipo);
    
    const link = document.createElement('a');
    if (tipo === 'corte') {
        link.href = `/api/cortes/download/${nomeArquivo}`;
    } else {
        link.href = `/api/minuta/download/${nomeArquivo}`;
    }
    link.download = nomeArquivo;
    link.click();
    
    // Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', 'download', {
            'event_category': 'pdf',
            'event_label': tipo
        });
    }
}

console.log('=== ARQUIVO APP.JS CARREGADO ===');
