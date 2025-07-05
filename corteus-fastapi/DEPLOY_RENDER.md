# 🚀 Configuração para Deploy no Render

## 📋 **Passos para Deploy Seguro**

### 1. **Configurar Variáveis de Ambiente no Render**

No painel do Render, vá em **Environment Variables** e configure:

```bash
# 🔐 SEGURANÇA JWT (OBRIGATÓRIO)
JWT_SECRET_KEY=gere_uma_chave_super_forte_aqui_32_bytes_minimo

# 🔑 SENHA DO ADMIN (OBRIGATÓRIO ALTERAR)
ADMIN_PASSWORD=sua_senha_admin_super_forte_aqui

# 🌐 AMBIENTE
RENDER=true
```

### 2. **Gerar Chave JWT Segura**

Execute este comando para gerar uma chave forte:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Ou use este site: https://generate-random.org/api-key-generator

### 3. **Deploy**

1. Push o código para o GitHub
2. Conecte o repositório no Render
3. Configure as variáveis de ambiente
4. Deploy!

## 🔒 **Recursos de Segurança Implementados**

- ✅ **JWT com assinatura criptográfica**
- ✅ **Cookies HTTPS em produção**
- ✅ **HTTPOnly cookies** (proteção XSS)
- ✅ **SameSite protection** (proteção CSRF)
- ✅ **Expiração automática** (24h)
- ✅ **Chaves seguras em variáveis de ambiente**

## 🛠️ **Como Usar em Produção**

1. Acesse seu site no Render
2. **Triplo clique no logo** para abrir o modal de login
3. Digite sua senha de admin configurada
4. Acesse o dashboard com segurança total!

## ⚠️ **IMPORTANTE**

- **NUNCA** use senhas fracas em produção
- **SEMPRE** gere uma nova `JWT_SECRET_KEY` para produção
- **NÃO** commite senhas no Git
- **ALTERE** a senha padrão do admin

## 🆘 **Troubleshooting**

### Problema: Cookie não funciona
- ✅ Verifique se o site está em HTTPS
- ✅ Confirme as variáveis de ambiente no Render

### Problema: Login não funciona
- ✅ Verifique a senha configurada no Render
- ✅ Confirme se `JWT_SECRET_KEY` está definida

### Problema: Dashboard vazio
- ✅ Aguarde alguns acessos para gerar dados
- ✅ Verifique se os eventos estão sendo salvos
