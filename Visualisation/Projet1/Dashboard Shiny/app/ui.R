library(shiny)
library(DT)
library(dplyr)
library(ggplot2)
library(lubridate)
library(ggiraph)




navbarPage(
  "Analyse des ventes de la librairie",
  
  tabPanel("Données",
           fluidPage(
             h2("Données des ventes"),
             tabsetPanel(
               tabPanel("Consommateurs" ,
                        sidebarLayout(
                          sidebarPanel(
                            h4("Informations sur les données"),
                            verbatimTextOutput("info_donnees_customers")  
                          ),
                          
                          mainPanel(
                            h3("Tableau des données consommateurs"),
                            DTOutput("customers"),
                            downloadButton("download_data_customers", "Télécharger les données CSV")
                          )
                        )),
               tabPanel("Produits" ,
                        sidebarLayout(
                          sidebarPanel(
                            h4("Informations sur les données"),
                            verbatimTextOutput("info_donnees_products")  
                          ),
                          
                          mainPanel(
                            h3("Tableau des données Produits"),
                            DTOutput("products"),
                            downloadButton("download_data_products", "Télécharger les données CSV")
                          )
                        )),
               tabPanel("Transactions" ,
                        sidebarLayout(
                          sidebarPanel(
                            h4("Informations sur les données"),
                            verbatimTextOutput("info_donnees_transactions")  
                          ),
                          
                          mainPanel(
                            h3("Tableau des données transactions"),
                            DTOutput("transactions"),
                            downloadButton("download_data_transactions", "Télécharger les données CSV")
                          )
                        )),
               tabPanel("Ensemble des données" ,
                        sidebarLayout(
                          sidebarPanel(
                            h4("Informations sur les données"),
                            verbatimTextOutput("info_donnees_fusion")  
                          ),
                          
                          mainPanel(
                            h3("Tableau des données consommateurs"),
                            DTOutput("fusion"),
                            downloadButton("download_data_fusion", "Télécharger les données CSV")
                          )
                        ))
             )
           )),
  
  
  tabPanel("Chiffres d'affaire",
           fluidPage(
             
             fluidRow(
               h3("Évolution du Chiffre d'Affaires"),
               selectInput("Plage_temporelle", "Choisissez la période :", 
                           choices = c("jour", "mois", "année")),
               
               # Filtre de date pour "Jour"
               conditionalPanel(
                 condition = "input.Plage_temporelle == 'jour'",
                 dateRangeInput("filtre_dates", "Sélectionnez la période :", 
                                start = "2021-09-01",
                                end = "2021-11-30",
                                format = "dd/mm/yyyy",
                                language = "fr")
               ),
               
               # Filtre de date pour "Mois"
               conditionalPanel(
                 condition = "input.Plage_temporelle == 'mois'",
                 dateRangeInput("filtre_dates2", "Sélectionnez la période :", 
                                start = "2021-01-01", 
                                end = "2023-02-28",
                                format = "dd/mm/yyyy",
                                language = "fr")
               ),
               
               # Filtre pour les années (si "Année" est sélectionné)
               conditionalPanel(
                 condition = "input.Plage_temporelle == 'année'",
                 selectInput("filtre_dates", "Sélectionner la plage d'années :", 
                             choices = c(2021, 2022, 2023))  # Années disponibles
               ),
               plotOutput("plot_chiffre_affaire"),
               conditionalPanel(
                 condition = "input.Plage_temporelle == 'année'",
                 actionButton("btn_ca", "Afficher le commentaire"),
                 textOutput("comment_ca")
               ),
               conditionalPanel(
                 condition = "input.Plage_temporelle == 'mois'",
                 actionButton("btn_ca2", "Afficher le commentaire"),
                 textOutput("comment_ca2")
               )
             ),
             
             fluidRow(
               column(2, 
                      selectInput("Plage_temporelle2", "Choisissez la période :", 
                                  choices = c("Mois", "Année"))
               ),
               column(5,
                      h3("CA Mensuel par Catégorie"),
                      plotOutput("plot_ca_par_categorie", height = "500px"),
                      actionButton("btn_ca_cat", "Afficher le commentaire"),
                      textOutput("comment_cacat") 
               ),
               column(5,
                      h3("CA Mensuel par Sexe"),
                      plotOutput("plot_ca_par_sexe", height = "500px"),
                      actionButton("btn_ca_sexe", "Afficher le commentaire"),
                      textOutput("comment_ca_sexe")
               )
             )
             
             
             
           )
  ),
  
  tabPanel("Produits",
           fluidPage(
             h2("Focus produits"),
             fluidRow(column(6,
                             fluidRow(
                               column(6, girafeOutput("top_10ca_prod"),
                                      actionButton("btn_top_10ca_prod", "Afficher le commentaire"),
                                      textOutput("comment_top_10ca_prod")),
                               column(6, girafeOutput("top_10qte_prod"),
                                      actionButton("btn_top_10qte_prod", "Afficher le commentaire"),
                                      textOutput("comment_top_10qte_prod"))
                             ),
                             fluidRow(
                               column(6, girafeOutput("flop_10ca_prod"),
                                      actionButton("btn_flop_10ca_prod", "Afficher le commentaire"),
                                      textOutput("comment_flop_10ca_prod")),
                               column(6, girafeOutput("flop_10qte_prod"),
                                      actionButton("btn_flop_10qte_prod", "Afficher le commentaire"),
                                      textOutput("comment_flop_10qte_prod"))
                             )
             ),
             column(6, plotOutput("distribution_vente"),
                    actionButton("btn_distribution_vente", "Afficher le commentaire"),
                    textOutput("comment_distribution_vente"))
             )
           )
  ),
  
  tabPanel("Clientèles",
           fluidPage(
             h2("Analyse de la clientèle")
           )),
  
  tabPanel("Catégorie",
           fluidPage(
             h2("Analyse des catégories de livres achetées")
           )),
  
  tabPanel("Sessions",
           fluidPage(
             h2("Analyse des Sessions"),
             fluidRow(
               actionButton("btn_distribution_vente", "Afficher le commentaire"),
               textOutput("comment_distribution_vente"),
               fluidRow(
                 column(6, girafeOutput("evolution_sessions")),
                 column(6, girafeOutput("sessions_par_mois"))
               ),
               fluidRow(
                 column(6, girafeOutput("sessions_par_heure")),
                 column(6, girafeOutput("sessions_par_sexe")
                 )
               )
             )
           )
  ),
  
  tabPanel("Prévisions",
           fluidPage(
             h2("Prévisions des ventes")
           ))
)
