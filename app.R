# Load necessary libraries
library(shiny)
library(httr)
library(rStrava)
library(dplyr)

# Source the credentials from keys.R
source("keys.R")

# Define the UI
ui <- fluidPage(
  titlePanel("Strava Authentication & Activities"),
  sidebarLayout(
    sidebarPanel(
      actionButton("auth_btn", "Authenticate with Strava"),
      actionButton("get_activities_btn", "Get Activities"),
      br(),
      br(),
      textOutput("auth_status")
    ),
    mainPanel(
      tableOutput("activities_table")
    )
  )
)

# Define the server logic
server <- function(input, output, session) {
  
  # Reactive value to store the authentication token
  auth_token <- reactiveVal(NULL)
  
  # Reactive value to store the activities
  activities <- reactiveVal(NULL)
  
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
  
  # Observe the get activities button
  observeEvent(input$get_activities_btn, {
    req(auth_token()) # Ensure the user is authenticated
    
    token <- auth_token()
    activities_data <- tryCatch(
      {
        # Fetch activities using the Strava API
        get_activity_list(
          stoken = token, 
          page_id = 1, 
          per_page = 30
        )
      },
      error = function(e) {
        showNotification("Failed to fetch activities.", type = "error")
        NULL
      }
    )
    
    if (!is.null(activities_data)) {
      # Process and store the activities data
      activities(
        activities_data %>%
          select(
            id,
            name,
            distance,
            moving_time,
            elapsed_time,
            total_elevation_gain
          )
      )
      showNotification("Activities successfully retrieved!", type = "message")
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
  
  # Display the activities table
  output$activities_table <- renderTable({
    req(activities()) # Ensure activities are available
    activities()
  })
}

# Run the app
shinyApp(ui = ui, server = server)
