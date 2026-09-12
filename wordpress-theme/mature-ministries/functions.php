<?php
/**
 * Mature Ministries theme bootstrap.
 *
 * Self-contained: registers its own "mm_sermon" post type and "mm_series"
 * taxonomy rather than depending on any specific sermon-manager plugin, so
 * this theme works on a plain WordPress install with whatever other plugins
 * the site owner already runs.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'MM_THEME_VERSION', '1.0.0' );

function mm_setup() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	register_nav_menus( array(
		'primary' => __( 'Primary Menu', 'mature-ministries' ),
	) );
}
add_action( 'after_setup_theme', 'mm_setup' );

function mm_enqueue_assets() {
	wp_enqueue_style(
		'mm-fonts',
		'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap',
		array(),
		null
	);
	wp_enqueue_style( 'mm-style', get_stylesheet_uri(), array(), MM_THEME_VERSION );

	if ( is_post_type_archive( 'mm_sermon' ) ) {
		wp_enqueue_script( 'mm-catalog', get_template_directory_uri() . '/assets/catalog.js', array(), MM_THEME_VERSION, true );
	}
}
add_action( 'wp_enqueue_scripts', 'mm_enqueue_assets' );

/**
 * "Sermon" post type + "Series" taxonomy.
 *
 * Video, transcript, and study-guide data are stored as plain post meta
 * (no ACF dependency) so an import (see the bundled WXR file) round-trips
 * cleanly through the core WordPress importer.
 */
function mm_register_sermon_cpt() {
	register_post_type( 'mm_sermon', array(
		'labels' => array(
			'name'          => __( 'Sermons', 'mature-ministries' ),
			'singular_name' => __( 'Sermon', 'mature-ministries' ),
			'add_new_item'  => __( 'Add New Sermon', 'mature-ministries' ),
			'edit_item'     => __( 'Edit Sermon', 'mature-ministries' ),
			'all_items'     => __( 'All Sermons', 'mature-ministries' ),
		),
		'public'       => true,
		'has_archive'  => 'sermons',
		'rewrite'      => array( 'slug' => 'sermons', 'with_front' => false ),
		'menu_icon'    => 'dashicons-microphone',
		'supports'     => array( 'title', 'editor', 'thumbnail', 'excerpt', 'custom-fields' ),
		'show_in_rest' => true,
	) );

	register_taxonomy( 'mm_series', 'mm_sermon', array(
		'labels' => array(
			'name'          => __( 'Series', 'mature-ministries' ),
			'singular_name' => __( 'Series', 'mature-ministries' ),
		),
		'public'       => true,
		'hierarchical' => false,
		'rewrite'      => array( 'slug' => 'series' ),
		'show_in_rest' => true,
	) );

	register_post_meta( 'mm_sermon', 'mm_youtube_id', array(
		'type' => 'string', 'single' => true, 'show_in_rest' => true,
	) );
	register_post_meta( 'mm_sermon', 'mm_sermon_date', array(
		'type' => 'string', 'single' => true, 'show_in_rest' => true,
	) );
	register_post_meta( 'mm_sermon', 'mm_source_link', array(
		'type' => 'string', 'single' => true, 'show_in_rest' => true,
	) );
	register_post_meta( 'mm_sermon', 'mm_audio_url', array(
		'type' => 'string', 'single' => true, 'show_in_rest' => true,
	) );
	// Serialized array of { label, url }.
	register_post_meta( 'mm_sermon', 'mm_pdf_guides', array(
		'type' => 'string', 'single' => true, 'show_in_rest' => false,
	) );
}
add_action( 'init', 'mm_register_sermon_cpt' );

/** Helper: decode the mm_pdf_guides meta into an array. */
function mm_get_guides( $post_id ) {
	$raw = get_post_meta( $post_id, 'mm_pdf_guides', true );
	if ( empty( $raw ) ) {
		return array();
	}
	$decoded = maybe_unserialize( $raw );
	return is_array( $decoded ) ? $decoded : array();
}

/** Helper: total published sermon count. */
function mm_sermon_count() {
	$counts = wp_count_posts( 'mm_sermon' );
	return isset( $counts->publish ) ? (int) $counts->publish : 0;
}
