import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import tempfile
import os

pytesseract.pytesseract.tesseract_cmd = os.path.join(os.path.dirname(__file__), "tesseract", "tesseract.exe")

st.set_page_config(
    page_title="Conversor PDF OCR",
    page_icon="📄",
    layout="centered"
)

st.title("📄 Conversor de PDF para Editável")
st.markdown("""
Esta aplicação converte PDFs digitalizados (imagens) em PDFs editáveis e pesquisáveis usando OCR (Reconhecimento Ótico de Caracteres).
""")

def pdf_ocr_para_editavel(pdf_entrada_bytes, progress_bar, status_text):
    """
    Converte um PDF digitalizado em PDF editável usando OCR
    """
    # Criar arquivo temporário para o PDF de entrada
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input:
        temp_input.write(pdf_entrada_bytes)
        temp_input_path = temp_input.name
    
    try:
        doc = fitz.open(temp_input_path)
        novo_pdf = fitz.open()
        total_paginas = len(doc)
        
        for i, pagina in enumerate(doc):
            status_text.text(f"Processando página {i + 1} de {total_paginas}...")
            
            # Converter página para imagem em alta resolução
            pix = pagina.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            # Aplicar OCR e gerar PDF pesquisável
            texto_pdf = pytesseract.image_to_pdf_or_hocr(img, extension='pdf', lang='por')
            temp_pdf = fitz.open("pdf", texto_pdf)
            novo_pdf.insert_pdf(temp_pdf)
            
            # Atualizar barra de progresso
            progress_bar.progress((i + 1) / total_paginas)
        
        # Salvar PDF convertido em bytes
        pdf_saida_bytes = novo_pdf.tobytes()
        
        novo_pdf.close()
        doc.close()
        
        return pdf_saida_bytes
        
    finally:
        # Limpar arquivo temporário
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)

# Interface de upload
st.markdown("### 📤 Upload do PDF")
uploaded_file = st.file_uploader(
    "Selecione um PDF digitalizado para converter",
    type=['pdf'],
    help="Escolha um arquivo PDF que contenha imagens digitalizadas"
)

if uploaded_file is not None:
    st.success(f"✅ Arquivo carregado: {uploaded_file.name}")
    
    # Informações do arquivo
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
    st.info(f"📊 Tamanho: {file_size:.2f} MB")
    
    # Botão de conversão
    if st.button("🔄 Converter para PDF Editável", type="primary"):
        st.markdown("### 🔄 Processamento")
        
        # Criar elementos de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Processar o PDF
            pdf_bytes = uploaded_file.getvalue()
            pdf_convertido = pdf_ocr_para_editavel(pdf_bytes, progress_bar, status_text)
            
            status_text.text("✅ Conversão concluída com sucesso!")
            st.success("🎉 PDF convertido com sucesso!")
            
            # Botão de download
            st.markdown("### 📥 Download")
            nome_saida = uploaded_file.name.replace('.pdf', '_editavel.pdf')
            
            st.download_button(
                label="⬇️ Baixar PDF Editável",
                data=pdf_convertido,
                file_name=nome_saida,
                mime="application/pdf",
                type="primary"
            )
            
        except Exception as e:
            st.error(f"❌ Erro ao processar o PDF: {str(e)}")
            status_text.text("❌ Erro no processamento")

else:
    st.info("👆 Faça upload de um PDF digitalizado para começar")

# Informações adicionais
with st.expander("ℹ️ Informações sobre OCR"):
    st.markdown("""
    **Como funciona:**
    - O aplicativo usa OCR (Reconhecimento Ótico de Caracteres) para ler o texto das imagens
    - Cada página é processada em alta resolução (300 DPI) para melhor qualidade
    - O texto reconhecido é incorporado ao PDF, tornando-o pesquisável e editável
    - Idioma configurado: Português
    
    **Dicas para melhor resultado:**
    - Use PDFs com imagens de boa qualidade
    - Certifique-se de que o texto está legível
    - Documentos com fontes maiores terão melhor reconhecimento
    """)
