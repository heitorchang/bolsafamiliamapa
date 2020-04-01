# Gerar uma pagina com OpenLayers contendo dados de
# http://www.dados.gov.br/dataset/bolsa-familia-misocial
# e dados geograficos de
# ftp://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/localidades

# SAO PAULO = 355030

import pickle
import datetime
import os
import glob
import csv
from pykml import parser

MUNICIPIOS_KML = "localidades.kml"
TOP_LIMIT = 100  # quantos municipios incluir
SUMMARY_FILE = "summary2019.js"

class Pagamento:
    # representa um pagamento e a data dela
    def __init__(self, d, v):
        self.data = d
        self.valor = v

    def __str__(self):
        return "{}: {}".format(self.data.strftime("%Y-%m-%d"), self.valor)

    def __repr__(self):
        return str(self)

    
class Municipio:
    # representa o name, lng, lat e serie de pagamentos
    def __init__(self, nome, uf, lng, lat):
        self.nome = nome
        self.uf = uf
        self.lng = lng
        self.lat = lat
        self.pagamentos = []

    def adicionarPagamento(self, d, v):
        self.pagamentos.append(v)

    def __str__(self):
        return "{} ({}) ({:.5f}, {:.5f}) [{} pagtos]".format(
            self.nome, self.uf, self.lng, self.lat,
            len(self.pagamentos)
        )

    def __repr__(self):
        return str(self)

    
def main():
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    except NameError:
        data_dir = "c:/Users/heitor/Desktop/code/bolsafamiliamapa/data/"
    kml_file = os.path.join(data_dir, MUNICIPIOS_KML)

    municipios = {}
    
    # process kml
    parse_kml_data(kml_file, municipios)

    # Bolsa Familia
    pbf_dir = os.path.join(data_dir, "pbf")

    os.chdir(pbf_dir)
    for f in sorted(glob.glob('*')):
        parse_pbf(f, municipios)

    # limit municipios to TOP_LIMIT
    ms = sorted(municipios.values(), key=lambda m: sum(m.pagamentos), reverse=True)

    ms = ms[:TOP_LIMIT]

    # check length of pagamentos are all equal
    lenpagtos = set()
    for m in ms:
        lenpagtos.add(len(m.pagamentos))

    assert len(lenpagtos) == 1
    
    json = jsonify(ms)

    try:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    except NameError:
        json_path = "c:/Users/heitor/Desktop/code/bolsafamiliamapa/" + SUMMARY_FILE

    with open(json_path, 'w', encoding="utf-8") as jsonfile:
        print(json, file=jsonfile)
        
    print("JSON written.")


def parse_kml_data(kml_file, municipios):
    with open(kml_file, encoding="utf-8") as f:
        doc = parser.parse(f)        
        folder = doc.getroot().Document.Folder

        for p in folder.Placemark:
            nome = p.name.text.title()
            simpledata = p.ExtendedData.SchemaData.SimpleData
            for sd in simpledata:
                if sd.attrib['name'] == "CD_GEOCODMU":
                    codigo_ibge = sd.text[:6]
                elif sd.attrib['name'] == "NM_UF":
                    uf = sd.text.title()
                elif sd.attrib['name'] == "LONG":
                    lng = float(sd.text)
                elif sd.attrib['name'] == "LAT":
                    lat = float(sd.text)
            municipios[codigo_ibge] = Municipio(nome, uf, lng, lat)


def parse_pbf(pbf_file, municipios):
    not_found = set()
    with open(pbf_file, encoding="utf-8", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data = datetime.datetime.strptime(row['anomes'], "%Y%m")
            try:
                municipios[row['ibge']].adicionarPagamento(data, float(row['valor_repassado_bolsa_familia']))
            except KeyError:
                if row['ibge'] not in not_found:
                    print("Municipio {} nao encontrado. Valor: {}".format(row['ibge'], float(row['valor_repassado_bolsa_familia'])))
                    not_found.add(row['ibge'])
        print("{} municipios nao encontrados.".format(len(not_found)))

        
def jsonify(municipios):
    json = "var municipios = ["
    json += ",\n".join(['["{}", {}, {}, {}]'.format(m.nome, m.lng, m.lat, m.pagamentos) for m in municipios])        
    json += "];"
    return json


if __name__ == '__main__':
    print("Generating SPA")
    json = main()
