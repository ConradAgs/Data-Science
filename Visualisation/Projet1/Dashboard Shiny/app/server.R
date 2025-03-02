
library(shiny)
library(DT)
library(dplyr)
library(ggplot2)
library(lubridate)
library(ggiraph)

function(input, output, session) {
  
  customers <- reactive({
    read.csv("../data/customers.csv", sep = ",", header = TRUE)  
  })
  
  products <- reactive({
    read.csv("../data/products.csv", sep = ",", header = TRUE)  
  })
  
  transactions <- reactive({
    read.csv("../data/transactions.csv", sep = ",", header = TRUE)  
  })
  
  fusion <- reactive({
    data <- read.csv("../data/fusion.csv", sep = ",", header = TRUE)  
    
    # Conversion des colonnes de dates
    data <- data %>%
      mutate(jour = as.Date(jour, format = "%d-%m-%Y"),
             prix = prix/1000)
    
    return(data)
  })
  
  output$info_donnees_customers <- renderText({
    df <- customers()
    paste("Nombre de lignes :", nrow(df), "\nNombre de colonnes :", ncol(df))
  })
  
  output$customers <- renderDT({
    datatable(customers(), options = list(pageLength = 10, autoWidth = TRUE))
  })
  
  output$download_data_customers <- downloadHandler(
    filename = function() {
      paste("donnees_", Sys.Date(), ".csv", sep = "")
    },
    content = function(file) {
      write.csv(customers(), file, row.names = FALSE)
    }
  )
  
  output$info_donnees_products <- renderText({
    df <- products()
    paste("Nombre de lignes :", nrow(df), "\nNombre de colonnes :", ncol(df))
  })
  
  output$products <- renderDT({
    datatable(products(), options = list(pageLength = 10, autoWidth = TRUE))
  })
  
  output$download_data_products <- downloadHandler(
    filename = function() {
      paste("donnees_", Sys.Date(), ".csv", sep = "")
    },
    content = function(file) {
      write.csv(products(), file, row.names = FALSE)
    }
  )
  
  output$info_donnees_transactions <- renderText({
    df <- transactions()
    paste("Nombre de lignes :", nrow(df), "\nNombre de colonnes :", ncol(df))
  })
  
  output$transactions <- renderDT({
    datatable(transactions(), options = list(pageLength = 10, autoWidth = TRUE))
  })
  
  output$download_data_transactions <- downloadHandler(
    filename = function() {
      paste("donnees_", Sys.Date(), ".csv", sep = "")
    },
    content = function(file) {
      write.csv(transactions(), file, row.names = FALSE)
    }
  )
  
  output$info_donnees_fusion <- renderText({
    df <- fusion()
    paste("Nombre de lignes :", nrow(df), "\nNombre de colonnes :", ncol(df))
  })
  
  output$fusion <- renderDT({
    datatable(fusion(), options = list(pageLength = 10, autoWidth = TRUE))
  })
  
  output$download_data_fusion <- downloadHandler(
    filename = function() {
      paste("donnees_", Sys.Date(), ".csv", sep = "")
    },
    content = function(file) {
      write.csv(fusion(), file, row.names = FALSE)
    }
  )
  
  #           ==================           # 
  
  # Filtrage des données de chiffre d'affaire en fonction de la plage temporelle
  filtered_data <- reactive({
    data <- fusion()
    
    # Si "jour" est sélectionné, filtrer en fonction de la plage de dates
    if (input$Plage_temporelle == "jour") {
      data <- data %>%
        filter(jour >= input$filtre_dates[1] &
                 jour <= input$filtre_dates[2])
    }
    
    # Si "mois" est sélectionné, filtrer en fonction du mois_annee
    if (input$Plage_temporelle == "mois") {
      data <- data %>%
        filter(jour >= input$filtre_dates2[1] &
                 jour <= input$filtre_dates2[2])
    }
    
    # Si "année" est sélectionné, filtrer en fonction de l'année
    if (input$Plage_temporelle == "année") {
      data <- data
    }
    
    return(data)
  })
  
  # Générer le graphique du chiffre d'affaire
  output$plot_chiffre_affaire <- renderPlot({
    data <- filtered_data()
    
    if (input$Plage_temporelle == "jour") {
      plot_data <- data %>%
        group_by(jour) %>%
        summarise(chiffre_affaire = sum(prix))
      ggplot(plot_data, aes(x = jour, y = chiffre_affaire)) +
        geom_line() +
        labs(title = "Chiffre d'Affaires par Jour", x = "Jour", y = "Chiffre d'Affaires (en k€)")
    } else if (input$Plage_temporelle == "mois") {
      plot_data <- data %>%
        group_by(mois_annee) %>%
        summarise(chiffre_affaire = sum(prix))
      ggplot(plot_data, aes(x = mois_annee, y = chiffre_affaire, group = 1)) +
        geom_line(color = "blue") +
        geom_point() +
        labs(title = "Chiffre d'Affaires par Mois", x = "Mois", y = "Chiffre d'Affaires (en k€)") +
        theme(axis.text.x = element_text(angle = 45, hjust = 1))
    } else if (input$Plage_temporelle == "année") {
      plot_data <- data %>%
        group_by(annee) %>%
        summarise(chiffre_affaire = sum(prix))
      ggplot(plot_data, aes(x = as.factor(annee), y = chiffre_affaire)) +
        geom_bar(stat = "identity", fill = 'brown') +
        labs(title = "Chiffre d'Affaires par Année", x = "Année", y = "Chiffre d'Affaires (en k€)")
    }
  })
  
  
  
  
  output$plot_ca_par_categorie <- renderPlot({
    data <- fusion()
    
    if (input$Plage_temporelle2 == "Mois") {
      plot_data <- data %>%
        group_by(mois_annee, categorie) %>%
        summarise(chiffre_affaire = sum(prix), .groups = "drop")
      
      ggplot(plot_data, aes(x = mois_annee, y = chiffre_affaire, fill = as.factor(categorie))) +
        geom_bar(stat = "identity") +  # Barres empilées
        labs(title = "Évolution Mensuelle du CA par Catégorie", x = "Mois", y = "Chiffre d'affaires en k€", fill = "Catégories :") +
        theme_minimal() +
        theme(axis.text.x = element_text(angle = 45, hjust = 1))
      
    } else if (input$Plage_temporelle2 == "Année") {
      plot_data <- data %>%
        group_by(annee, categorie) %>%
        summarise(chiffre_affaire = sum(prix), .groups = "drop")
      
      ggplot(plot_data, aes(x = as.factor(annee), y = chiffre_affaire, fill = as.factor(categorie))) +
        geom_bar(stat = "identity") +  # Barres empilées
        labs(title = "CA Annuel par Catégorie", x = "Année", y = "Chiffre d'affaires en k€", fill = "Catégories :") +
        theme_minimal()
    }
  })
  
  
  output$plot_ca_par_sexe <- renderPlot({
    data <- fusion()
    
    if (input$Plage_temporelle2 == "Mois") {
      plot_data <- data %>%
        group_by(mois_annee, sexe) %>%
        summarise(chiffre_affaire = sum(prix), .groups = "drop")
      
      ggplot(plot_data, aes(x = mois_annee, y = chiffre_affaire, fill = sexe)) +
        geom_bar(stat = "identity") +  # Barres empilées
        labs(title = "Évolution Mensuelle du CA par Sexe", x = "Mois", y = "Chiffre d'affaires en k€", fill = "Sexe") +
        theme_minimal() +
        theme(axis.text.x = element_text(angle = 45, hjust = 1))
      
    } else if (input$Plage_temporelle2 == "Année") {
      plot_data <- data %>%
        group_by(annee, sexe) %>%
        summarise(chiffre_affaire = sum(prix), .groups = "drop")
      
      ggplot(plot_data, aes(x = as.factor(annee), y = chiffre_affaire, fill = sexe)) +
        geom_bar(stat = "identity") +  # Barres empilées
        labs(title = "CA Annuel par Sexe", x = "Année", y = "Chiffre d'affaires en k€", fill = "Sexe") +
        theme_minimal()
    }
  })
  
  
  #           ==================           # 
  
  
  
  produits_data <- reactive({
    fusion() %>%
      group_by(id_produit) %>%
      summarise(
        chiffre_affaire = sum(prix, na.rm = TRUE),
        quantite = n()
      ) %>%
      arrange(desc(chiffre_affaire))
  })
  
  # Top 10 CA
  output$top_10ca_prod <- renderGirafe({
    data <- produits_data() %>% head(10)
    
    p <- ggplot(data, aes(x = reorder(id_produit, chiffre_affaire), y = chiffre_affaire)) +
      geom_bar_interactive(stat = "identity", fill = "green",
                           aes(tooltip = paste("Produit:", id_produit, "<br>CA:", chiffre_affaire, "k€"))) +
      coord_flip() +
      labs(title = "Top 10 en Chiffre d'Affaires", x = NULL, y = "Chiffre d'Affaires (k€)")
    
    girafe(ggobj = p)
  })
  
  # Flop 10 CA
  output$flop_10ca_prod <- renderGirafe({
    data <- produits_data() %>% tail(10)
    
    p <- ggplot(data, aes(x = reorder(id_produit, chiffre_affaire), y = chiffre_affaire)) +
      geom_bar_interactive(stat = "identity", fill = "red",
                           aes(tooltip = paste("Produit:", id_produit, "<br>CA:", chiffre_affaire, "k€"))) +
      coord_flip() +
      labs(title = "Flop 10 en Chiffre d'Affaires", x = NULL, y = "Chiffre d'Affaires (k€)")
    
    girafe(ggobj = p)
  })
  
  # Top 10 Quantité
  output$top_10qte_prod <- renderGirafe({
    data <- produits_data() %>% arrange(desc(quantite)) %>% head(10)
    
    p <- ggplot(data, aes(x = reorder(id_produit, quantite), y = quantite)) +
      geom_bar_interactive(stat = "identity", fill = "green",
                           aes(tooltip = paste("Produit:", id_produit, "<br>Quantité:", quantite, "u"))) +
      coord_flip() +
      labs(title = "Top 10 en Quantité", x = NULL, y = "Quantité Vendue (u)")
    
    girafe(ggobj = p)
  })
  
  # Flop 10 Quantité
  output$flop_10qte_prod <- renderGirafe({
    data <- produits_data() %>% arrange(quantite) %>% head(10)
    
    p <- ggplot(data, aes(x = reorder(id_produit, quantite), y = quantite)) +
      geom_bar_interactive(stat = "identity", fill = "red",
                           aes(tooltip = paste("Produit:", id_produit, "<br>Quantité:", quantite, "u"))) +
      coord_flip() +
      labs(title = "Flop 10 en Quantité", x = NULL, y = "Quantité Vendue (u)")
    
    girafe(ggobj = p)
  })
  
  output$distribution_vente <- renderPlot({
    data <- produits_data()
    ggplot(data, aes(x = quantite)) +
      geom_histogram(binwidth = 50, fill = "blue", color = "black", alpha = 0.7) +
      labs(title = "Distribution du nombre de ventes", x = "Quantité vendue", y = "Nombre de produits") +
      theme_minimal()
  })
  
  
  #           ==================           # 
  
  output$evolution_sessions <- renderGirafe({
    data <- fusion() %>%
      group_by(mois_annee) %>%
      summarise(nb_sessions = n_distinct(id_session), .groups = "drop")
    
    p <- ggplot(data, aes(x = mois_annee, y = nb_sessions, group = 1)) +
      geom_line_interactive(color = "blue", size = 1, 
                            aes(tooltip = paste("Mois/Année:", mois_annee, "<br>Sessions:", nb_sessions))) +
      geom_point_interactive(color = "darkblue", 
                             aes(tooltip = paste("Mois/Année:", mois_annee, "<br>Sessions:", nb_sessions))) +
      labs(title = "Évolution du Nombre de Sessions", x = "Temps", y = "Nombre de Sessions") +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1))
    
    girafe(ggobj = p)
  })
  
  output$sessions_par_mois <- renderGirafe({
    data <- fusion() %>%
      group_by(mois) %>%
      summarise(nb_sessions = n_distinct(id_session), .groups = "drop")
    
    p <- ggplot(data, aes(x = factor(mois, levels = 1:12), y = nb_sessions, fill = as.factor(mois))) +
      geom_bar_interactive(stat = "identity", width = 0.7, 
                           aes(tooltip = paste("Mois:", month.name[mois], "<br>Sessions:", nb_sessions))) +
      labs(title = "Répartition des Sessions par Mois", x = "Mois", y = "Nombre de Sessions") +
      scale_x_discrete(labels = month.name) + 
      theme_minimal() +
      theme(legend.position = "none", axis.text.x = element_text(angle = 45, hjust = 1))
    
    girafe(ggobj = p)
  })
  
  
  
  output$sessions_par_heure <- renderGirafe({
    data <- fusion() %>%
      mutate(heure = hour(date_achat)) %>%
      group_by(heure) %>%
      summarise(nb_sessions = n_distinct(id_session), .groups = "drop")
    
    p <- ggplot(data, aes(x = heure, y = nb_sessions, fill = as.factor(heure))) +
      geom_bar_interactive(stat = "identity", width = 0.7, 
                           aes(tooltip = paste("Heure :", heure, "<br>Sessions :", nb_sessions))) +
      labs(title = "Répartition des Sessions par Heure", x = "Heure", y = "Nombre de Sessions") +
      scale_x_continuous(breaks = 0:23) +
      theme_minimal() +
      theme(legend.position = "none")
    
    girafe(ggobj = p)
  })
  
  
  
  output$sessions_par_sexe <- renderGirafe({
    data <- fusion() %>%
      group_by(sexe) %>%
      summarise(nb_sessions = n_distinct(id_session), .groups = "drop")
    
    p <- ggplot(data, aes(x = sexe, y = nb_sessions, fill = sexe)) +
      geom_bar_interactive(stat = "identity", width = 0.5, 
                           aes(tooltip = paste("Sexe :", sexe, "<br>Sessions :", nb_sessions))) +
      labs(title = "Répartition des Sessions par Sexe", x = "Sexe", y = "Nombre de Sessions") +
      theme_minimal() +
      theme(legend.position = "none")
    
    girafe(ggobj = p)
  })
  
  
  
}
