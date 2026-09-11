<?php if ( ! defined( 'ABSPATH' ) ) exit; ?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<header class="site-header">
	<div class="container site-header__row">
		<a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="brand">
			<span class="brand__mark mono">MM</span>
			<span class="brand__name"><?php bloginfo( 'name' ); ?></span>
		</a>
		<nav class="site-nav mono">
			<a href="<?php echo esc_url( get_post_type_archive_link( 'mm_sermon' ) ); ?>">Catalog</a>
			<a href="<?php echo esc_url( home_url( '/#about' ) ); ?>">About</a>
		</nav>
	</div>
</header>
<main>
