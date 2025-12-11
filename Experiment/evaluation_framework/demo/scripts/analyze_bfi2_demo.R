# Analyze BFI-2 data using Fingerprinting, EGA, Alpha, and Wasserstein distance.
# This is just a demo designed to showcase the evaluation framework. The actual implementation should be adjusted accordingly based on your real ouput data format.

if (!require(psych)) stop("Package 'psych' is required")
if (!require(EGAnet)) stop("Package 'EGAnet' is required")

DATA_DIR <- "Experiment/evaluation_framework/demo/outputs/simulated_data"
OUTPUT_DIR <- "Experiment/evaluation_framework/demo/outputs/results"
RESULTS_DIR <- OUTPUT_DIR

if (!dir.exists(OUTPUT_DIR)) {
  dir.create(OUTPUT_DIR, recursive = TRUE)
}

# Fingerprinting
get_upper_tri <- function(cormat) {
  cormat[upper.tri(cormat)]
}

calc_cosine_similarity <- function(vec1, vec2) {
  sum(vec1 * vec2) / (sqrt(sum(vec1^2)) * sqrt(sum(vec2^2)))
}

calc_wasserstein_1d <- function(dist1, dist2) {
  # CDFs
  cdf1 <- cumsum(dist1)
  cdf2 <- cumsum(dist2)
  sum(abs(cdf1[1:4] - cdf2[1:4]))
}

calc_alignment_score <- function(w_dist, max_dist = 4) {
  1 - (w_dist / max_dist)
}

# --- Main Logic ---

message("Starting BFI-2 Analysis...")

# Load Data
data_files <- list.files(DATA_DIR, pattern = "*.csv", full.names = TRUE)
if (length(data_files) == 0) {
  stop("No data files found in ", DATA_DIR)
}

datasets <- lapply(data_files, read.csv)
names(datasets) <- tools::file_path_sans_ext(basename(data_files))

message("Loaded datasets: ", paste(names(datasets), collapse = ", "))

# --- Dimension 1: Structural Similarity ---

# A. Fingerprints Similarity
message("\n--- Computing Fingerprints ---")
fingerprints <- lapply(datasets, function(df) {
  cor_mat <- cor(df, method = "pearson")
  get_upper_tri(cor_mat)
})

# Pairwise comparisons (Reference: human_src)
ref_name <- "llm_src"
if (ref_name %in% names(datasets)) {
  similarities <- do.call(rbind, lapply(names(datasets), function(name) {
    if (name == ref_name) return(NULL)
    sim <- calc_cosine_similarity(fingerprints[[ref_name]], fingerprints[[name]])
    data.frame(comparison = paste0(ref_name, "_vs_", name), similarity = sim)
  }))
  
  print(similarities)
  write.csv(similarities, file.path(RESULTS_DIR, "fingerprint_similarity.csv"), row.names = FALSE)
} else {
  warning("Reference dataset 'human_src' not found for fingerprint comparison.")
}

# B. Internal Consistency (Cronbach's Alpha)
message("\n--- Computing Cronbach's Alpha ---")
get_domains <- function(df) {
  unique(sub("_\\d+$", "", colnames(df)))
}

alpha_results_list <- lapply(names(datasets), function(name) {
  df <- datasets[[name]]
  domains <- get_domains(df)
  
  res_list <- lapply(domains, function(dom) {
    cols <- grep(paste0("^", dom), colnames(df))
    items <- df[, cols]
    
    a_res <- psych::alpha(items, check.keys = FALSE, warnings = FALSE)$total$raw_alpha
    
    data.frame(dataset = name, domain = dom, alpha = a_res)
  })
  do.call(rbind, res_list)
})

alpha_results <- do.call(rbind, alpha_results_list)
print(alpha_results)
write.csv(alpha_results, file.path(RESULTS_DIR, "cronbach_alpha.csv"), row.names = FALSE)

# C. EGA
message("\n--- Running EGA ---")
ega_summary_list <- lapply(names(datasets), function(name) {
  message(sprintf("Running EGA for %s...", name))
  df <- datasets[[name]]
  
  tryCatch({
    ega_obj <- EGAnet::EGA(df, plot.EGA = TRUE) 
    
    pdf_path <- file.path(RESULTS_DIR, paste0("ega.", name, ".pdf"))
    pdf(pdf_path, width = 10, height = 10)
    print(ega_obj$plot.EGA)
    dev.off()
    message("Saved EGA plot to ", pdf_path)
    
    n_dim <- ega_obj$n.dim

    data.frame(dataset = name, n_dimensions = n_dim)
  }, error = function(e) {
    message("EGA failed for ", name, ": ", e$message)
    return(NULL)
  })
})

ega_summary <- do.call(rbind, ega_summary_list)
print(ega_summary)
write.csv(ega_summary, file.path(RESULTS_DIR, "ega_summary.csv"), row.names = FALSE)

# --- Dimension 2: Behavioral Alignment (Wasserstein) ---
message("\n--- Computing Wasserstein Alignment ---")

if (ref_name %in% names(datasets)) {
  ref_data <- datasets[[ref_name]]
  
  alignment_summary_list <- lapply(names(datasets), function(name) {
    if (name == ref_name) return(NULL)
    target_data <- datasets[[name]]
    
    item_results <- do.call(rbind, lapply(colnames(ref_data), function(item) {
      # Get distributions
      t1 <- table(factor(ref_data[[item]], levels = 1:5))
      p1 <- as.numeric(t1) / sum(t1)
      
      t2 <- table(factor(target_data[[item]], levels = 1:5))
      p2 <- as.numeric(t2) / sum(t2)
      
      w_dist <- calc_wasserstein_1d(p1, p2)
      align <- calc_alignment_score(w_dist)
      
      data.frame(
        item = item,
        domain = sub("_\\d+$", "", item),
        wasserstein = w_dist,
        alignment = align
      )
    }))
    
    item_results$comparison <- paste0(ref_name, "_vs_", name)
    
    # Save per-item results
    write.csv(item_results, file.path(RESULTS_DIR, paste0("alignment_per_item_", name, ".csv")), row.names = FALSE)
    
    # Aggregate by domain
    agg <- aggregate(alignment ~ domain, data = item_results, FUN = mean)
    colnames(agg)[2] <- "avg_alignment"
    agg$comparison <- paste0(ref_name, "_vs_", name)
    
    return(agg)
  })
  
  alignment_results <- do.call(rbind, alignment_summary_list)
  print(alignment_results)
  write.csv(alignment_results, file.path(RESULTS_DIR, "alignment_by_domain_summary.csv"), row.names = FALSE)
}

message("\nAnalysis Complete. Results in ", RESULTS_DIR)
