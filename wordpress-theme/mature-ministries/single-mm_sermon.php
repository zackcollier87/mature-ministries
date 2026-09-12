<?php
/** Sermon detail — series/date head, video embed, guide downloads, full transcript. */
if ( ! defined( 'ABSPATH' ) ) exit;
get_header();

while ( have_posts() ) : the_post();
	$id     = get_the_ID();
	$date   = get_post_meta( $id, 'mm_sermon_date', true );
	$yt     = get_post_meta( $id, 'mm_youtube_id', true );
	$link   = get_post_meta( $id, 'mm_source_link', true );
	$guides = mm_get_guides( $id );
	$audio  = get_post_meta( $id, 'mm_audio_url', true );
	$terms  = get_the_terms( $id, 'mm_series' );
	?>
	<article class="container sermon">
		<nav class="mono breadcrumb"><a href="<?php echo esc_url( get_post_type_archive_link( 'mm_sermon' ) ); ?>">&larr; Catalog</a></nav>

		<header class="sermon__head">
			<?php if ( ! empty( $terms ) && ! is_wp_error( $terms ) ) : ?>
				<p class="mono sermon__series"><?php echo esc_html( implode( ' · ', wp_list_pluck( $terms, 'name' ) ) ); ?></p>
			<?php endif; ?>
			<h1><?php the_title(); ?></h1>
			<p class="mono sermon__date tabular-nums"><?php echo esc_html( $date ? date_i18n( 'M d, Y', strtotime( $date ) ) : '' ); ?></p>
		</header>

		<?php if ( $yt ) : ?>
			<div class="video-frame">
				<iframe
					src="https://www.youtube-nocookie.com/embed/<?php echo esc_attr( $yt ); ?>"
					title="<?php the_title_attribute(); ?>"
					loading="lazy"
					allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
					allowfullscreen
				></iframe>
			</div>
		<?php endif; ?>

		<?php if ( $audio ) : ?>
			<div class="audio-block">
				<p class="mono audio-block__label">LISTEN</p>
				<audio controls preload="none" src="<?php echo esc_url( $audio ); ?>">
					Your browser does not support the audio element. <a href="<?php echo esc_url( $audio ); ?>">Download the audio</a> instead.
				</audio>
				<a class="mono audio-block__download" href="<?php echo esc_url( $audio ); ?>" download>Download MP3 &darr;</a>
			</div>
		<?php endif; ?>

		<?php if ( ! empty( $guides ) ) : ?>
			<div class="guides">
				<p class="mono guides__label">STUDY GUIDE</p>
				<ul class="guides__list">
					<?php foreach ( $guides as $g ) : ?>
						<li>
							<a class="mono guide-link" href="<?php echo esc_url( $g['url'] ); ?>">
								<?php echo esc_html( $g['label'] ); ?> <span aria-hidden="true">&darr;</span>
							</a>
						</li>
					<?php endforeach; ?>
				</ul>
			</div>
		<?php endif; ?>

		<?php
		$content = get_the_content();
		if ( trim( $content ) !== '' ) :
			?>
			<div class="transcript">
				<p class="mono transcript__label">TRANSCRIPT</p>
				<?php the_content(); ?>
			</div>
		<?php endif; ?>

		<?php if ( $link ) : ?>
			<footer class="sermon__source mono">
				Originally published at <a href="<?php echo esc_url( $link ); ?>">theheritagechurch.org</a>
			</footer>
		<?php endif; ?>
	</article>
<?php endwhile;

get_footer();
