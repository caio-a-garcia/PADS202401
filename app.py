from shiny.express import input, render, ui
import matplotlib.pyplot as plt
from shiny import ui, render
import pandas as pd
import numpy as np


# Obter os dados
customers = pd.read_csv("https://github.com/fshirahige/deploy_dataviz/raw/main/olist_customers_dataset.csv")
geolocation = pd.read_csv("https://github.com/fshirahige/deploy_dataviz/raw/main/olist_geolocation_dataset.csv")
orders = pd.read_csv("https://github.com/fshirahige/deploy_dataviz/raw/main/olist_orders_dataset.csv")
order_items = pd.read_csv("https://github.com/fshirahige/deploy_dataviz/raw/main/olist_order_items_dataset.csv")
order_payments = pd.read_csv("https://github.com/fshirahige/deploy_dataviz/raw/main/olist_order_payments_dataset.csv")
order_reviews = pd.read_csv("https://github.com/fshirahige/deploy_dataviz/raw/main/olist_order_reviews_dataset.csv")
products = pd.read_csv("https://github.com/fshirahige/deploy_dataviz/raw/main/olist_products_dataset.csv")
sellers = pd.read_csv("https://github.com/fshirahige/deploy_dataviz/raw/main/olist_sellers_dataset.csv")

# Transformando as colunas de data (de object para data)
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'])
orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'])


orders['prazo_estimado'] = (orders['order_estimated_delivery_date'] - orders['order_approved_at']).dt.days
orders['prazo_realizado'] = (orders['order_delivered_customer_date'] - orders['order_approved_at']).dt.days
orders['atraso'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days

# 11 Crie um metodo para agrupar todas as diferentes latitudes e longitudes que um determinado CEP
# possui para um valor unico por CEP. Dica Use a funcao group_by e aggragate
geolocation_agrupado = geolocation.groupby('geolocation_zip_code_prefix').agg({'geolocation_lat':'mean', 'geolocation_lng':'mean'}).reset_index()

# 12 mesclando os dataframes
#Mesclando os df de orders e customers
df = pd.merge(orders, customers, on='customer_id', how='left')
#Mesclando os df de orders e items
df = pd.merge(df, order_items, on='order_id', how='left')
#Mesclando os df de orders e sellers
df = pd.merge(df, sellers, on='seller_id', how='left')
#Mesclando os df de orders e payments
df = pd.merge(df, order_payments, on='order_id', how='left')
#Mesclando os df de orders e reviews
df = pd.merge(df, order_reviews, on='order_id', how='left')
#Mesclando os df de orders e products
df = pd.merge(df, products, on='product_id', how='left')
#Mesclando os df de orders e geolocation (customer = geolocation_zip_code_prefix_x)
df = pd.merge(df, geolocation_agrupado, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix' , how='left')

# Criar um dataframe com os dados de compras de clientes do RJ
df_rj = df[df['customer_state'] == 'RJ']

#Definir as variaveis que poderão ser escolhidas
frete_estado = df_rj.groupby('seller_state')['freight_value'].mean()
review_estado = df_rj.groupby('seller_state')['review_score'].mean()
vendas_estado = df_rj.groupby('seller_state')['payment_value'].sum()

#Criar dataframe com as series vendas_estado, review_estado, frete_estado
df_estado = pd.DataFrame({
    'Vendas': vendas_estado,
    'Review': review_estado,
    'Frete': frete_estado
})

ui.input_selectize(
    "var", "Selecione a Variavel",
    choices=["Frete", "Review", "Vendas"])


@render.plot
def bar():
    plt.bar(df_estado[input.var()].sort_values(ascending=False).index, df_estado[input.var()].sort_values(ascending=False), color='#a5cee2')
    indice_destacado =  vendas_estado.index.get_loc('SP')
    cores = ['#1f78b4', '#1f78b4']
    plt.bar(df_estado.index[indice_destacado], df_estado[input.var()][indice_destacado], color=cores)
    plt.title(input.var()+' por Estado')