// Layout rewards slider
const slides = document.querySelectorAll(".loyalty-brand-card");

let counter = 0;

slides.forEach((slide, index) => {
  slide.style.left = `${index * 170}px`;
});

const goPrev = () => {
  if (counter !== 0) {
    counter--;
    slideImage();
  }
};

const goNext = () => {
  if (counter < slides.length - 4) {
    counter++;
    slideImage();
  }
};

const slideImage = () => {
  slides.forEach((slide, index) => {
    slide.style.transform = `translateX(-${counter * 170}px)`;
  });
};

// Recommended Brands slider
const slides1 = document.querySelectorAll(".recommended-brands-card");

let counter1 = 0;

slides1.forEach((slide, index) => {
  slide.style.left = `${index * 170}px`;
});

const goPrev1 = () => {
  if (counter1 !== 0) {
    counter1--;
    slideImage1();
  }
};

const goNext1 = () => {
  if (counter1 < slides1.length - 4) {
    counter1++;
    slideImage1();
  }
};

const slideImage1 = () => {
  slides1.forEach((slide, index) => {
    slide.style.transform = `translateX(-${counter1 * 170}px)`;
  });
};

// Brands Popup
const lightbox = document.querySelector(".lightbox");
const overlay = document.querySelector("#overlay");

const openLightbox1 = async (e) => {
  const brandName = e.querySelector("button").innerText;
  try {
    // Fetch the JSON data from the server
    const response = await fetch(
      "http://localhost:5000/database/updated_brands_loyalty_rewards.json"
    );
    if (!response.ok) {
      throw new Error("Failed to fetch loyalty brands data");
    }
    const loyaltyBrandsData = await response.json();
    // Find the matching brand in the JSON data
    const brandData = loyaltyBrandsData.find(
      (item) => item.brand === brandName
    );
    // Get the loyalty rewards message (if the brand is found)
    const loyaltyRewardsMessage = brandData
      ? brandData.loyalty_rewards
      : "No rewards found for this brand.";
    // Update the lightbox content
    lightbox.querySelector("p").innerText = loyaltyRewardsMessage;

    // Open the lightbox and overlay
    lightbox.classList.remove("invisible");
    overlay.style.display = "block";
  } catch (error) {
    console.error("Error fetching loyalty brands data:", error);
  }
};

const openLightbox2 = async (e) => {
  const brandName = e.querySelector("button").innerText;
  try {
    // Fetch the JSON data from the server
    const response = await fetch(
      "http://localhost:5000/database/discount.json"
    );
    if (!response.ok) {
      throw new Error("Failed to fetch recommended brands data");
    }

    const rb_data = await response.json();

    // Find the corresponding offer message
    let offerMessage = "No offer found for this brand.";

    // Iterate through the "Brand" object to find the matching brand
    for (const key in rb_data.Brand) {
      if (rb_data.Brand[key] === brandName) {
        // If a match is found, get the corresponding offer from the "Offer" object
        offerMessage = rb_data.Offer[key];
        break;
      }
    }

    console.log("Offer Message:", offerMessage); // Log the offer message

    // Update the lightbox content
    lightbox.querySelector("p").innerText = offerMessage;

    // Open the lightbox and overlay
    lightbox.classList.remove("invisible");
    overlay.style.display = "block";
  } catch (error) {
    console.error("Error fetching loyalty brands data:", error);
  }
};

const closeLightbox = () => {
  lightbox.classList.add("invisible");
  overlay.style.display = "none";
};
