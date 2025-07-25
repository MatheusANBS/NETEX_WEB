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
        showError(errorElement, `Formato inválido: ${e.message}. Use números separados por vírgula, espaço ou quebra de linha. Exemplo: "200x20, 1500, x3"`);
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
    const partes = str.split(/[,\s\n\r]+/)
                     .map(s => s.trim())
                     .filter(s => s !== '');
    
    const numeros = [];
    
    for (const parte of partes) {
        // Formato: 200x20 (valor x quantidade)
        if (parte.includes('x')) {
            const [valor, quantidade] = parte.split('x');
            
            if (valor && quantidade) {
                // Formato: 200x20
                const val = parseInt(valor);
                const qty = parseInt(quantidade);
                if (isNaN(val) || isNaN(qty) || val <= 0 || qty <= 0) {
                    throw new Error(`Formato inválido: ${parte}`);
                }
                // Adicionar o valor 'qty' vezes
                for (let i = 0; i < qty; i++) {
                    numeros.push(val);
                }
            } else if (valor && !quantidade) {
                // Formato: x20 (quantidade apenas, usar último valor)
                const qty = parseInt(valor);
                if (isNaN(qty) || qty <= 0) {
                    throw new Error(`Quantidade inválida: ${parte}`);
                }
                if (numeros.length === 0) {
                    throw new Error('Use "x" apenas após informar pelo menos um valor');
                }
                const ultimoValor = numeros[numeros.length - 1];
                // Adicionar o último valor mais 'qty-1' vezes (pois já existe 1)
                for (let i = 0; i < qty - 1; i++) {
                    numeros.push(ultimoValor);
                }
            } else if (!valor && quantidade) {
                // Formato: x20 (quantidade apenas)
                const qty = parseInt(quantidade);
                if (isNaN(qty) || qty <= 0) {
                    throw new Error(`Quantidade inválida: ${parte}`);
                }
                if (numeros.length === 0) {
                    throw new Error('Use "x" apenas após informar pelo menos um valor');
                }
                const ultimoValor = numeros[numeros.length - 1];
                // Adicionar o último valor mais 'qty-1' vezes (pois já existe 1)
                for (let i = 0; i < qty - 1; i++) {
                    numeros.push(ultimoValor);
                }
            }
        } else {
            // Formato normal: apenas número
            const num = parseInt(parte);
            if (isNaN(num) || num <= 0) {
                throw new Error(`Valor inválido: ${parte}`);
            }
            numeros.push(num);
        }
    }
    
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

// Validar formulário completo com indicação específica de erros
function validarFormulario() {
    console.log('Validando formulário...');
    
    const dados = coletarDados();
    console.log('Dados coletados:', dados);
    
    const erros = [];
    
    // Validar SS
    if (!dados.ss.trim()) {
        erros.push('SS é obrigatório');
    } else if (!validarSS()) {
        erros.push('SS está em formato incorreto (deve ser XXXX/YYYY)');
    }
    
    // Validar SK
    if (!dados.sk.trim()) {
        erros.push('SK é obrigatório');
    } else if (!validarSK()) {
        erros.push('SK está em formato incorreto (deve ser EST-XXX ou TU-XXX)');
    }
    
    // Validar Código do Material
    if (!dados.cod_material.trim()) {
        erros.push('Código do Material é obrigatório');
    } else if (!validarCodMaterial()) {
        erros.push('Código do Material deve ter exatamente 10 dígitos');
    }
    
    // Validar Cortes Desejados
    if (!dados.cortes_desejados || dados.cortes_desejados.length === 0) {
        erros.push('Cortes Desejados é obrigatório');
    } else if (!validarCortes()) {
        erros.push('Cortes Desejados contém valores inválidos');
    }
    
    // Validações específicas por modo
    if (dados.modo === 'Automático') {
        if (!dados.comprimento_barra || dados.comprimento_barra <= 0) {
            erros.push('Comprimento da Barra é obrigatório no modo automático');
        }
    } else if (dados.modo === 'Manual') {
        if (!dados.barras_disponiveis || dados.barras_disponiveis.length === 0) {
            erros.push('Barras Disponíveis é obrigatório no modo manual');
        } else if (!validarBarras()) {
            erros.push('Barras Disponíveis contém valores inválidos');
        }
    }
    
    // Se há erros, exibir todos
    if (erros.length > 0) {
        const mensagemErro = 'Corrija os seguintes erros:\n• ' + erros.join('\n• ');
        showAlert('error', mensagemErro);
        console.log('Erros de validação:', erros);
        return false;
    }
    
    console.log('Formulário válido');
    return true;
}

// Validação específica para relatório de corte
function validarFormularioCorte() {
    console.log('Validando formulário para corte...');
    
    const dados = coletarDados();
    const erros = [];
    
    // Validações básicas
    if (!validarFormularioBase(dados, erros)) {
        return false;
    }
    
    // Validações específicas para corte
    if (dados.modo === 'Automático') {
        if (!dados.comprimento_barra || dados.comprimento_barra <= 0) {
            erros.push('Comprimento da Barra é obrigatório para gerar relatório de corte no modo automático');
        }
        if (dados.comprimento_barra && dados.comprimento_barra < Math.max(...dados.cortes_desejados)) {
            erros.push('Comprimento da Barra deve ser maior que o maior corte desejado');
        }
    } else {
        if (!dados.barras_disponiveis || dados.barras_disponiveis.length === 0) {
            erros.push('Barras Disponíveis é obrigatório para gerar relatório de corte no modo manual');
        }
    }
    
    if (erros.length > 0) {
        const mensagemErro = 'Não é possível gerar o relatório de corte:\n• ' + erros.join('\n• ');
        showAlert('error', mensagemErro);
        return false;
    }
    
    return true;
}

// Validação específica para relatório de minuta
function validarFormularioMinuta() {
    console.log('Validando formulário para minuta...');
    
    const dados = coletarDados();
    const erros = [];
    
    // Validações básicas
    if (!validarFormularioBase(dados, erros)) {
        return false;
    }
    
    // Validações específicas para minuta
    if (dados.cortes_desejados.some(c => c > 6000)) {
        erros.push('Cortes maiores que 6000mm não são permitidos para relatório de minuta');
    }
    
    if (erros.length > 0) {
        const mensagemErro = 'Não é possível gerar o relatório de minuta:\n• ' + erros.join('\n• ');
        showAlert('error', mensagemErro);
        return false;
    }
    
    return true;
}

// Função auxiliar para validações básicas
function validarFormularioBase(dados, erros) {
    // Validar SS
    if (!dados.ss.trim()) {
        erros.push('SS é obrigatório');
        focusField('ss');
    } else if (!validarSS()) {
        erros.push('SS está em formato incorreto (deve ser XXXX/YYYY)');
        focusField('ss');
    }
    
    // Validar SK
    if (!dados.sk.trim()) {
        erros.push('SK é obrigatório');
        focusField('sk');
    } else if (!validarSK()) {
        erros.push('SK está em formato incorreto (deve ser EST-XXX ou TU-XXX)');
        focusField('sk');
    }
    
    // Validar Código do Material
    if (!dados.cod_material.trim()) {
        erros.push('Código do Material é obrigatório');
        focusField('cod_material');
    } else if (!validarCodMaterial()) {
        erros.push('Código do Material deve ter exatamente 10 dígitos');
        focusField('cod_material');
    }
    
    // Validar Cortes Desejados
    if (!dados.cortes_desejados || dados.cortes_desejados.length === 0) {
        erros.push('Cortes Desejados é obrigatório');
        focusField('cortes_desejados');
    } else if (!validarCortes()) {
        erros.push('Cortes Desejados contém valores inválidos. Use formato: "200x20" para quantidades ou números separados por vírgula');
        focusField('cortes_desejados');
    }
    
    if (erros.length > 0) {
        const mensagemErro = 'Corrija os seguintes erros:\n• ' + erros.join('\n• ');
        showAlert('error', mensagemErro);
        return false;
    }
    
    return true;
}

// Função para focar no campo com erro
function focusField(fieldId) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.focus();
        field.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Gerar relatório de corte
async function gerarCorte() {
    console.log('=== GERANDO CORTE ===');
    
    if (!validarFormularioCorte()) {
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
    
    if (!validarFormularioMinuta()) {
        console.log('Validação falhou');
        return;
    }
    
    const dados = coletarDados();
    
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

// Alert genérico com suporte a múltiplas linhas
function showAlert(type, message) {
    console.log('Exibindo alerta:', type, message);
    
    // Criar toast notification
    const alert = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-600' : 'bg-blue-600';
    alert.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-4 rounded-lg shadow-lg z-50 transform transition-all duration-300 max-w-md`;
    
    // Formatear mensagem para múltiplas linhas
    const formattedMessage = message.replace(/\n/g, '<br>');
    
    alert.innerHTML = `
        <div class="flex items-start">
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-2 mt-1 flex-shrink-0"></i>
            <div class="text-sm leading-relaxed">${formattedMessage}</div>
        </div>
    `;
    
    document.body.appendChild(alert);
    
    // Animar entrada
    setTimeout(() => alert.classList.add('translate-x-0'), 100);
    
    // Remover após 8 segundos (mais tempo para ler múltiplas linhas)
    setTimeout(() => {
        alert.classList.add('translate-x-full');
        setTimeout(() => {
            if (document.body.contains(alert)) {
                document.body.removeChild(alert);
            }
        }, 300);
    }, 8000);
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
