// PDF Book Viewer - Main JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Add PDF icons to all PDF links
  const pdfLinks = document.querySelectorAll(".pdf-link");
  pdfLinks.forEach((link) => {
    const iconSpan = document.createElement("span");
    iconSpan.className = "pdf-icon";
    link.prepend(iconSpan);
  });

  // Add hover effect to folder containers
  const folderContainers = document.querySelectorAll(".folder-container");
  folderContainers.forEach((container) => {
    container.addEventListener("mouseenter", function () {
      this.style.transition = "all 0.3s ease";
    });
  });

  // Make folders collapsible (optional future feature)
  const folderHeaders = document.querySelectorAll("h2");
  folderHeaders.forEach((header) => {
    header.classList.add("folder-header");
    header.addEventListener("click", function () {
      const folderContent = this.nextElementSibling;
      if (
        folderContent &&
        (folderContent.tagName === "UL" || folderContent.tagName === "P")
      ) {
        folderContent.style.display =
          folderContent.style.display === "none" ? "block" : "none";
        this.classList.toggle("collapsed");
      }
    });
  });

  // Add a simple search functionality
  function createSearchBox() {
    const container = document.querySelector(".container");
    const header = document.querySelector(".header");

    const searchContainer = document.createElement("div");
    searchContainer.className = "search-container";
    searchContainer.style.marginBottom = "20px";
    searchContainer.style.display = "flex";

    const searchInput = document.createElement("input");
    searchInput.type = "text";
    searchInput.placeholder = "Search PDFs...";
    searchInput.className = "search-input";
    searchInput.style.padding = "10px";
    searchInput.style.borderRadius = "4px";
    searchInput.style.border = "1px solid #ddd";
    searchInput.style.marginRight = "10px";
    searchInput.style.flex = "1";

    const searchButton = document.createElement("button");
    searchButton.textContent = "Search";
    searchButton.className = "search-button";
    searchButton.style.padding = "10px 15px";
    searchButton.style.backgroundColor = "#3498db";
    searchButton.style.color = "white";
    searchButton.style.border = "none";
    searchButton.style.borderRadius = "4px";
    searchButton.style.cursor = "pointer";

    searchContainer.appendChild(searchInput);
    searchContainer.appendChild(searchButton);

    // Insert after tag filters
    const tagFilters = document.querySelector(".tag-filters");
    if (tagFilters) {
      tagFilters.insertAdjacentElement("afterend", searchContainer);
    } else {
      header.insertAdjacentElement("afterend", searchContainer);
    }

    // Simple search functionality
    function performSearch(query) {
      query = query.toLowerCase();
      const allLinks = document.querySelectorAll(".pdf-link");

      allLinks.forEach((link) => {
        const fileName = link.textContent.trim().toLowerCase();
        const listItem = link.parentElement;

        if (fileName.includes(query)) {
          listItem.style.display = "block";
          // Highlight the matching part
          const startIndex = fileName.indexOf(query);
          if (startIndex !== -1) {
            const beforeMatch = link.textContent.substring(0, startIndex);
            const match = link.textContent.substring(
              startIndex,
              startIndex + query.length
            );
            const afterMatch = link.textContent.substring(
              startIndex + query.length
            );

            // Only modify the text content, keep the icon
            const iconElement = link.querySelector(".pdf-icon");
            link.innerHTML = "";
            if (iconElement) link.appendChild(iconElement);

            link.appendChild(document.createTextNode(beforeMatch));
            const highlight = document.createElement("span");
            highlight.style.backgroundColor = "yellow";
            highlight.style.fontWeight = "bold";
            highlight.textContent = match;
            link.appendChild(highlight);
            link.appendChild(document.createTextNode(afterMatch));
          }
        } else {
          listItem.style.display = "none";
        }
      });

      // Check if any files are visible in each folder
      const folderContainers = document.querySelectorAll(".folder-container");
      folderContainers.forEach((container) => {
        const visibleItems = container.querySelectorAll(
          'li[style="display: block;"]'
        );
        container.style.display = visibleItems.length > 0 ? "block" : "none";
      });
    }

    // Add event listeners for search
    searchButton.addEventListener("click", function () {
      performSearch(searchInput.value);
    });

    searchInput.addEventListener("keyup", function (e) {
      if (e.key === "Enter") {
        performSearch(this.value);
      }
      // Reset search on empty input
      if (this.value === "") {
        const allListItems = document.querySelectorAll("li");
        const allFolders = document.querySelectorAll(".folder-container");

        allListItems.forEach((item) => (item.style.display = "block"));
        allFolders.forEach((folder) => (folder.style.display = "block"));

        // Reset highlighted text
        const allLinks = document.querySelectorAll(".pdf-link");
        allLinks.forEach((link) => {
          if (link.innerHTML.includes("<span")) {
            const plainText = link.textContent;
            const iconElement = link.querySelector(".pdf-icon");
            link.innerHTML = "";
            if (iconElement) link.appendChild(iconElement);
            link.appendChild(document.createTextNode(plainText));
          }
        });
      }
    });
  }

  // Enhanced search that also considers tags
  function enhanceSearchWithTags() {
    const searchInput = document.querySelector(".search-input");
    const searchButton = document.querySelector(".search-button");

    if (!searchInput || !searchButton) return;

    // Override the click handler
    searchButton.addEventListener("click", function () {
      const query = searchInput.value.toLowerCase();

      // Special tag search syntax: "tag:finished" or "tag:in_progress"
      if (query.startsWith("tag:")) {
        const tagQuery = query.substring(4).trim();
        highlightTaggedBooks(tagQuery);
      }
    });
  }

  // Function to highlight books with specific tags
  function highlightTaggedBooks(tagQuery) {
    const allTags = document.querySelectorAll(".tag");
    const matchingTags = Array.from(allTags).filter((tag) =>
      tag.textContent.toLowerCase().includes(tagQuery)
    );

    const allItems = document.querySelectorAll("li");
    allItems.forEach((item) => {
      item.style.display = "none";
      item.classList.remove("highlighted");
    });

    matchingTags.forEach((tag) => {
      const listItem = tag.closest("li");
      if (listItem) {
        listItem.style.display = "block";
        listItem.classList.add("highlighted");

        // Add subtle highlight effect
        const link = listItem.querySelector(".pdf-link");
        if (link) {
          link.style.backgroundColor = "rgba(52, 152, 219, 0.1)";
        }
      }
    });

    // Make sure folders with matches are visible
    const folderContainers = document.querySelectorAll(".folder-container");
    folderContainers.forEach((container) => {
      const hasVisibleItems =
        container.querySelectorAll('li[style="display: block;"]').length > 0;
      container.style.display = hasVisibleItems ? "block" : "none";
    });
  }

  // Initialize the search box
  createSearchBox();

  // Enhance search with tag functionality
  enhanceSearchWithTags();

  // Close tag dropdowns when clicking elsewhere
  document.addEventListener("click", function (event) {
    if (
      !event.target.matches(".tag-dropdown-button") &&
      !event.target.closest(".tag-dropdown-content")
    ) {
      const openDropdowns = document.querySelectorAll(".tag-dropdown.show");
      openDropdowns.forEach((dropdown) => dropdown.classList.remove("show"));
    }
  });

  // Highlight tags in URL if any
  const urlParams = new URLSearchParams(window.location.search);
  const highlightTag = urlParams.get("highlight");
  if (highlightTag) {
    highlightTaggedBooks(highlightTag);
  }
});
