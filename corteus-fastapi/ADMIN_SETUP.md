# 🔐 Configuração da Senha de Admin no Render

## Como Configurar no Render:

### 1. **Acesse o Dashboard do Render**
   - Vá para [render.com](https://render.com)
   - Faça login na sua conta
   - Selecione o seu serviço (corteus-fastapi)

### 2. **Adicionar Variável de Ambiente**
   - No painel do serviço, vá para **"Environment"** 
   - Clique em **"Add Environment Variable"**
   - Configure:
     ```
     Key: ADMIN_PASSWORD
     Value: SuaSenhaSecretaAqui123!
     ```

### 3. **Exemplos de Senhas Seguras:**
   ```
   ADMIN_PASSWORD=Corteus@2024!Admin
   ADMIN_PASSWORD=MinhaSenhaSecreta#789
   ADMIN_PASSWORD=Analytics@Corteus2024
   ```

### 4. **Deploy Automático**
   - Após salvar, o Render fará o deploy automaticamente
   - A nova senha será ativada em alguns minutos

### 5. **Verificar se Funcionou**
   - Acesse o seu site
   - Clique 3 vezes na logo
   - Digite a senha que você configurou
   - O botão "Analytics" deve aparecer

## 🛡️ **Dicas de Segurança:**

- ✅ Use senhas com pelo menos 12 caracteres
- ✅ Combine letras, números e símbolos
- ✅ Não compartilhe a senha
- ✅ Mude periodicamente

## 🔧 **Para Desenvolvimento Local:**

1. Crie um arquivo `.env` na raiz do projeto:
   ```
   ADMIN_PASSWORD=sua_senha_de_teste
   ```

2. O arquivo `.env` já está no `.gitignore`, então não será commitado

## 📋 **Senha Padrão (Temporária):**

Se você não configurar a variável de ambiente, a senha padrão será: `admin123`

**⚠️ IMPORTANTE:** Configure sua própria senha no Render o quanto antes!
