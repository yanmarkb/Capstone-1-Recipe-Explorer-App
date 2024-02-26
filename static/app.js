$(document).ready(function () {
	$(".favorite-icon").each(function () {
		var mealId = $(this).data("meal-id");
		var icon = $(this);
		$.ajax({
			url: "/meal/is_favorited/" + mealId,
			type: "GET",
			success: function (response) {
				console.log("isFavorited response", response);
				if (response.isFavorited) {
					icon.addClass("favorited");
					icon.removeClass("not-favorited");
				} else {
					icon.removeClass("favorited");
					icon.addClass("not-favorited");
				}
			},
		});
	});

	$(".favorite-icon").click(function (event) {
		event.preventDefault();
		var mealId = $(this).data("meal-id");
		var icon = $(this);
		var isFavorited = icon.hasClass("favorited");
		console.log("isFavorited before click", isFavorited);
		var url = "/meal/toggle_favorite/" + mealId;
		$.ajax({
			url: url,
			type: "POST",
			success: function (response) {
				console.log("toggleFavorite response", response);
				if (response.isFavorited) {
					icon.addClass("favorited");
					icon.removeClass("not-favorited");
				} else {
					icon.removeClass("favorited");
					icon.addClass("not-favorited");
				}
			},
		});
	});

	document.querySelectorAll(".dropbtn").forEach((button) => {
		button.addEventListener("click", () => {
			const dropdownContent = button.nextElementSibling;
			dropdownContent.classList.toggle("show");
			button.classList.toggle("open");
		});
	});
});

const carouselImages = document.querySelectorAll(".carousel-image");

Promise.all(
	Array.from({ length: carouselImages.length }, () =>
		fetch("https://www.themealdb.com/api/json/v1/1/random.php")
			.then((response) => response.json())
			.then((data) => data.meals[0].strMealThumb)
	)
).then((imageUrls) => {
	carouselImages.forEach((image, index) => {
		image.src = imageUrls[index];
	});

	let activeIndex = 0;
	setInterval(() => {
		carouselImages[activeIndex].classList.remove("active");
		activeIndex = (activeIndex + 1) % carouselImages.length;
		carouselImages[activeIndex].classList.add("active");
	}, 3000);
});

document.querySelector(".dropdown-btn").addEventListener("click", function () {
	var navLinks = document.querySelectorAll("nav a");
	for (var i = 0; i < navLinks.length; i++) {
		if (navLinks[i].style.display === "none") {
			navLinks[i].style.display = "block";
		} else {
			navLinks[i].style.display = "none";
		}
	}
});

document
	.querySelector(".footer-dropdown-btn")
	.addEventListener("click", function () {
		var footerLinks = document.querySelectorAll(".footer-content p");
		for (var i = 0; i < footerLinks.length; i++) {
			if (footerLinks[i].style.display === "none") {
				footerLinks[i].style.display = "block";
			} else {
				footerLinks[i].style.display = "none";
			}
		}
	});
