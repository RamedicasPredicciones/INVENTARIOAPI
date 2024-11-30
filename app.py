if faltantes_file:
    with st.spinner("Procesando archivos..."):
        # Leer el archivo de faltantes cargado
        faltantes_df = pd.read_excel(faltantes_file)
        
        # Mostrar las columnas cargadas para depuración
        st.write("Columnas del archivo de faltantes cargado:", list(faltantes_df.columns))
        
        # Normalizar columnas
        faltantes_df.columns = faltantes_df.columns.str.lower().str.strip()
        
        # Verificar que las columnas necesarias estén presentes
        columnas_necesarias = {'cur', 'codart', 'faltante', 'embalaje'}
        if not columnas_necesarias.issubset(faltantes_df.columns):
            st.error(
                f"El archivo de faltantes debe contener las columnas: {', '.join(columnas_necesarias)}. "
                f"Las columnas detectadas fueron: {', '.join(faltantes_df.columns)}."
            )
        else:
            # Si las columnas están presentes, proceder con el procesamiento
            if inventario is not None:
                alternativas = procesar_faltantes(
                    faltantes_df,
                    inventario,
                    columnas_adicionales=['nombre', 'laboratorio', 'presentacion'],
                    bodega_seleccionada=None,
                )
                
                st.success("¡Alternativas generadas exitosamente!")
                st.write("Aquí tienes las alternativas generadas:")
                st.dataframe(alternativas)
                
                # Botón para descargar el archivo de alternativas
                st.header("Descargar Alternativas")
                
                @st.cache_data
                def convertir_a_excel(df):
                    import io
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Alternativas")
                    processed_data = output.getvalue()
                    return processed_data

                alternativas_excel = convertir_a_excel(alternativas)
                st.download_button(
                    label="Descargar archivo de alternativas",
                    data=alternativas_excel,
                    file_name="alternativas_generadas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.error("No se pudo cargar el inventario. Por favor, intente de nuevo.")
