from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import uuid

ufs = ['SC', 'AM', 'CE']

for uf in ufs:

    uf_input = uf
    servico = Service(ChromeDriverManager().install())

    # Inicializando o driver do Selenium
    driver = webdriver.Chrome(service=servico)

    # Acessando o site
    driver.get("https://www2.correios.com.br/sistemas/buscacep/buscaFaixaCep.cfm")

    # Selecionando a UF = SC
    uf = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "UF")))
    uf.click()
    WebDriverWait(uf, 10).until(EC.presence_of_element_located((By.XPATH, f"//option[@value='{uf_input}']"))).click()

    # Clicando no botão de Buscar
    #driver.find_element_by_xpath("//div[@class='btnform']/input[@type='submit']").click()
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Geral"]/div/div/div[4]/input'))).click()

    # Criando lista para armazenar os dados
    dados = []
    first_page = True
    localidades_adicionadas = set()
    while True:
        # Obtendo o HTML da página
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Coletando dados da tabela
        if first_page:
            tabela = soup.find_all("table", {"class": "tmptabela"})[1]
            first_page = False
        else:
            tabela = soup.find("table", {"class": "tmptabela"})
        linhas = tabela.find_all("tr")
        for linha in linhas:
            colunas = linha.find_all("td")
            # Aqui Verifica se há algum valor dentro da lista antes de tentar acessar a posição
            if len(colunas) > 0:
                localidade = colunas[0].text
                faixa_cep = colunas[1].text
                # Verifica se o dado não existe
                if localidade not in localidades_adicionadas:
                    localidades_adicionadas.add(localidade)
                    unique_id = str(uuid.uuid4())
                    dados.append({"id": unique_id,"localidade": localidade, "faixa_cep": faixa_cep})
        # Verificando se existem mais páginas
        try:
            proxima_pagina = driver.find_element('xpath','/html/body/div[1]/div[3]/div[2]/div/div/div[2]/div[2]/div[2]/div[5]/a')
            proxima_pagina.click()
        except:
            break


        # Salvando dados em arquivo JSON com codificação utf-8
        with open("dados.jsonl", "a", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)


# Fechando o driver do Selenium
driver.quit()
