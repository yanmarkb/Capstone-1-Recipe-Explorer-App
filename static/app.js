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
		});
	});
});
