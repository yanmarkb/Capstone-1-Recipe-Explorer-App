$(document).ready(function () {
	$(".favorite-icon").each(function () {
		var mealId = $(this).data("meal-id");
		var icon = $(this);
		$.ajax({
			url: "/meal/is_favorited/" + mealId,
			type: "GET",
			success: function (response) {
				if (response.isFavorited) {
					icon.css("color", "red");
				} else {
					icon.css("color", "grey");
				}
			},
		});
	});
});

$(".favorite-icon").click(function () {
	var mealId = $(this).data("meal-id");
	var isFavorited = $(this).css("color") === "rgb(255, 0, 0)";
	var url = "/meal/toggle_favorite/" + mealId;
	$.ajax({
		url: url,
		type: "POST",
		success: function (response) {
			if (response.success) {
				$(this).css(
					"color",
					isFavorited ? "rgb(128, 128, 128)" : "rgb(255, 0, 0)"
				);
			}
		}.bind(this),
	});
});

document.querySelectorAll(".dropbtn").forEach((button) => {
	button.addEventListener("click", () => {
		const dropdownContent = button.nextElementSibling;
		dropdownContent.classList.toggle("show");
	});
});

$(".favorite-icon").click(function () {
	var mealId = $(this).data("meal-id");
	$.post("/meal/toggle_favorite/" + mealId, function () {
		location.reload();
	});
});
