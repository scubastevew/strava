# Load necessary libraries
library(shiny)
library(httr)
library(strava)

# Source the credentials from keys.R
source("keys.R")

# Define the UI
ui <- fluidPage(
  titlePanel("Strava Authentication"),
  sidebarLayout(
    sidebarPanel(
      actionButton("auth_btn", "Authenticate with Strava")
    ),
    mainPanel(
      textOutput("auth_status"),
      textOutput("token_info")
    )
  )
)

# Define the server logic
server <- function(input, output, session) {
  
  # Reactive value to store the authentication token
  auth_token <- reactiveVal(NULL)
  
  # Observe the authentication button
  observeEvent(input$auth_btn, {
    # Authenticate with Strava
    token <- tryCatch(
      {
        strava_oauth(
          app_name, 
          app_client_id, 
          app_secret, 
          app_scope = "activity:read_all"
        )
      },
      error = function(e) {
        showNotification("Authentication failed. Check your credentials.", type = "error")
        NULL
      }
    )
    
    if (!is.null(token)) {
      # Save the token to the reactive value
      auth_token(token)
      showNotification("Successfully authenticated!", type = "message")
    }
  })
  
  # Display authentication status
  output$auth_status <- renderText({
    if (is.null(auth_token())) {
      "Not authenticated."
    } else {
      "Authenticated successfully!"
    }
  })
  
  # Display token information
  output$token_info <- renderText({
    token <- auth_token()
    if (is.null(token)) {
      return("No token available.")
    }
    paste("Access Token:", token$credentials$access_token)
  })
}

# Run the app
shinyApp(ui = ui, server = server)
